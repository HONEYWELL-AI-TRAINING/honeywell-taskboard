import { afterEach, describe, expect, it, vi } from 'vitest'
import api from '../api'
import * as taskService from '../taskService'

vi.mock('../api')

afterEach(() => vi.clearAllMocks())

describe('taskService', () => {
  it('omits the status param when filter is "all"', async () => {
    api.get.mockResolvedValue({ data: [] })
    await taskService.listTasks('all')
    expect(api.get).toHaveBeenCalledWith('/api/tasks', { params: {} })
  })

  it('passes status through when a filter is set', async () => {
    api.get.mockResolvedValue({ data: [] })
    await taskService.listTasks('todo')
    expect(api.get).toHaveBeenCalledWith('/api/tasks', { params: { status: 'todo' } })
  })

  it('lists deleted tasks with an optional status filter', async () => {
    api.get.mockResolvedValue({ data: [] })
    await taskService.listTasks('done', true)
    expect(api.get).toHaveBeenCalledWith('/api/tasks', {
      params: { status: 'done', deleted: true },
    })
  })

  it('gets a deleted task only when explicitly requested', async () => {
    api.get.mockResolvedValue({ data: { id: 3 } })
    await taskService.getTask(3, true)
    expect(api.get).toHaveBeenCalledWith('/api/tasks/3', {
      params: { includeDeleted: true },
    })
  })

  it('gets an active task without changing the existing request shape', async () => {
    api.get.mockResolvedValue({ data: { id: 3 } })
    await taskService.getTask(3)
    expect(api.get).toHaveBeenCalledWith('/api/tasks/3')
  })

  it('posts a new task and returns the created record', async () => {
    api.post.mockResolvedValue({ data: { id: 7, title: 'x' } })
    const result = await taskService.createTask({ title: 'x' })
    expect(api.post).toHaveBeenCalledWith('/api/tasks', { title: 'x' })
    expect(result).toEqual({ id: 7, title: 'x' })
  })

  it('deletes by id', async () => {
    api.delete.mockResolvedValue({})
    await taskService.deleteTask(3)
    expect(api.delete).toHaveBeenCalledWith('/api/tasks/3')
  })

  it('restores a deleted task', async () => {
    api.post.mockResolvedValue({})
    await taskService.restoreTask(3)
    expect(api.post).toHaveBeenCalledWith('/api/tasks/3/restore')
  })

  it('permanently deletes only through the explicit permanent flag', async () => {
    api.delete.mockResolvedValue({})
    await taskService.permanentlyDeleteTask(3)
    expect(api.delete).toHaveBeenCalledWith('/api/tasks/3', {
      params: { permanent: true },
    })
  })
})
