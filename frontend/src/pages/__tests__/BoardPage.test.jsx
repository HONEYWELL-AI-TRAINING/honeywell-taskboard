import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as taskService from '../../services/taskService'
import BoardPage from '../BoardPage'

vi.mock('../../services/taskService', () => ({
  listTasks: vi.fn(),
  createTask: vi.fn(),
  updateTask: vi.fn(),
  deleteTask: vi.fn(),
  restoreTask: vi.fn(),
  permanentlyDeleteTask: vi.fn(),
}))

const activeTask = {
  id: 1,
  title: 'Active task',
  status: 'todo',
  assignee: null,
}

const deletedTask = {
  id: 2,
  title: 'Deleted task',
  status: 'done',
  assignee: null,
}

afterEach(() => {
  vi.clearAllMocks()
  vi.restoreAllMocks()
})

describe('BoardPage deleted-task view', () => {
  it('loads active tasks by default and switches to deleted tasks', async () => {
    taskService.listTasks
      .mockResolvedValueOnce([activeTask])
      .mockResolvedValueOnce([deletedTask])
    const user = userEvent.setup()
    render(<BoardPage />)

    expect(await screen.findByText('Active task')).toBeInTheDocument()
    expect(taskService.listTasks).toHaveBeenNthCalledWith(1, 'all', false)

    await user.click(screen.getByRole('button', { name: 'View deleted tasks' }))

    expect(await screen.findByText('Deleted task')).toBeInTheDocument()
    expect(taskService.listTasks).toHaveBeenNthCalledWith(2, 'all', true)
    expect(screen.queryByLabelText('Title')).not.toBeInTheDocument()
  })

  it('restores a deleted task and refreshes the deleted list', async () => {
    taskService.listTasks.mockResolvedValue([deletedTask])
    taskService.restoreTask.mockResolvedValue({})
    const user = userEvent.setup()
    render(<BoardPage />)

    await user.click(await screen.findByRole('button', { name: 'View deleted tasks' }))
    await user.click(await screen.findByRole('button', { name: 'Restore' }))

    expect(taskService.restoreTask).toHaveBeenCalledWith(deletedTask.id)
    await waitFor(() => expect(taskService.listTasks).toHaveBeenCalledTimes(3))
  })

  it('requires confirmation before permanently deleting a task', async () => {
    taskService.listTasks.mockResolvedValue([deletedTask])
    taskService.permanentlyDeleteTask.mockResolvedValue({})
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const user = userEvent.setup()
    render(<BoardPage />)

    await user.click(await screen.findByRole('button', { name: 'View deleted tasks' }))
    await user.click(await screen.findByRole('button', { name: 'Delete permanently' }))

    expect(window.confirm).toHaveBeenCalled()
    expect(taskService.permanentlyDeleteTask).toHaveBeenCalledWith(deletedTask.id)
  })

  it('does not permanently delete when confirmation is declined', async () => {
    taskService.listTasks.mockResolvedValue([deletedTask])
    vi.spyOn(window, 'confirm').mockReturnValue(false)
    render(<BoardPage />)

    fireEvent.click(await screen.findByRole('button', { name: 'View deleted tasks' }))
    fireEvent.click(await screen.findByRole('button', { name: 'Delete permanently' }))

    expect(taskService.permanentlyDeleteTask).not.toHaveBeenCalled()
  })
})
