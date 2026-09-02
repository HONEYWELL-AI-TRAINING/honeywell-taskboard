import { describe, expect, it, vi } from 'vitest'
import api from '../api'
import { createComment, deleteComment, getCommentCount, listComments } from '../commentService'

vi.mock('../api', () => ({
  default: { delete: vi.fn(), get: vi.fn(), post: vi.fn() },
}))

describe('commentService', () => {
  it('delegates comment requests to the nested API endpoints', async () => {
    api.get.mockResolvedValueOnce({ data: { count: 2 } }).mockResolvedValueOnce({ data: [{ id: 1 }] })
    api.post.mockResolvedValue({ data: { id: 2 } })

    expect(await getCommentCount(4)).toBe(2)
    expect(await listComments(4)).toEqual([{ id: 1 }])
    expect(await createComment(4, { author: 'Sam', text: 'Note' })).toEqual({ id: 2 })
    await deleteComment(4, 2)

    expect(api.get).toHaveBeenNthCalledWith(1, '/api/tasks/4/comments/count')
    expect(api.get).toHaveBeenNthCalledWith(2, '/api/tasks/4/comments')
    expect(api.post).toHaveBeenCalledWith('/api/tasks/4/comments', { author: 'Sam', text: 'Note' })
    expect(api.delete).toHaveBeenCalledWith('/api/tasks/4/comments/2')
  })
})