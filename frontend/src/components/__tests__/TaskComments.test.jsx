import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import TaskComments from '../TaskComments'

const comments = [
  { id: 1, author: 'Sam', text: 'First note', created_at: '2026-01-01T12:00:00' },
  { id: 2, author: 'Priya', text: 'Second note', created_at: '2026-01-02T12:00:00' },
]

describe('TaskComments', () => {
  it('renders comments oldest first with author and timestamp', () => {
    render(<TaskComments comments={comments} onCreate={vi.fn()} onDelete={vi.fn()} />)

    expect(screen.getByText('Sam')).toBeInTheDocument()
    expect(screen.getByText('Priya')).toBeInTheDocument()
    expect(screen.getAllByRole('time')).toHaveLength(2)
    expect(screen.getAllByText(/note/)[0]).toHaveTextContent('First note')
  })

  it('submits an author and non-blank comment', async () => {
    const onCreate = vi.fn().mockResolvedValue(undefined)
    render(<TaskComments comments={[]} onCreate={onCreate} onDelete={vi.fn()} />)

    await userEvent.type(screen.getByLabelText('Author'), 'Priya')
    await userEvent.type(screen.getByLabelText('Comment'), 'Please review')
    await userEvent.click(screen.getByRole('button', { name: 'Post comment' }))

    expect(onCreate).toHaveBeenCalledWith({ author: 'Priya', text: 'Please review' })
  })

  it('does not submit missing author or whitespace-only text', async () => {
    const onCreate = vi.fn()
    render(<TaskComments comments={[]} onCreate={onCreate} onDelete={vi.fn()} />)

    await userEvent.type(screen.getByLabelText('Comment'), '   ')
    await userEvent.click(screen.getByRole('button', { name: 'Post comment' }))

    expect(onCreate).not.toHaveBeenCalled()
    expect(screen.getByText('Author and comment text are required.')).toBeInTheDocument()
  })

  it('deletes a displayed comment', async () => {
    const onDelete = vi.fn().mockResolvedValue(undefined)
    render(<TaskComments comments={comments} onCreate={vi.fn()} onDelete={onDelete} />)

    await userEvent.click(screen.getByRole('button', { name: 'Delete comment 1' }))

    expect(onDelete).toHaveBeenCalledWith(1)
  })
})