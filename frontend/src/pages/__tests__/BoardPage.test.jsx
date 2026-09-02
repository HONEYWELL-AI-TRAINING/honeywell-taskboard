import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import BoardPage from '../BoardPage'

vi.mock('../../services/taskService', () => ({
  createTask: vi.fn(),
  deleteTask: vi.fn(),
  listTasks: vi.fn().mockResolvedValue([{
    id: 1, title: 'Write tests', description: null, status: 'todo', assignee: null,
  }]),
  updateTask: vi.fn(),
}))

vi.mock('../../services/commentService', () => ({
  createComment: vi.fn(),
  deleteComment: vi.fn(),
  getCommentCount: vi.fn().mockResolvedValue(2),
  listComments: vi.fn(),
}))

describe('BoardPage', () => {
  it('loads a comment count for each task', async () => {
    render(<BoardPage />)

    expect(await screen.findByText('2 comments')).toBeInTheDocument()
  })
})