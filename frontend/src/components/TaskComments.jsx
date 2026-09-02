import { useState } from 'react'

export default function TaskComments({ comments, onCreate, onDelete }) {
  const [author, setAuthor] = useState('')
  const [text, setText] = useState('')
  const [error, setError] = useState(null)

  async function handleSubmit(event) {
    event.preventDefault()
    if (!author || !text.trim()) {
      setError('Author and comment text are required.')
      return
    }
    setError(null)
    await onCreate({ author, text })
    setText('')
  }

  return (
    <section className="task-comments" aria-label="Comments">
      {comments.map((comment) => (
        <article className="comment" key={comment.id}>
          <div><strong>{comment.author}</strong> <time dateTime={comment.created_at}>{new Date(comment.created_at).toLocaleString()}</time></div>
          <p>{comment.text}</p>
          <button onClick={() => onDelete(comment.id)} aria-label={`Delete comment ${comment.id}`}>Delete</button>
        </article>
      ))}
      <form onSubmit={handleSubmit} className="comment-form">
        <label>Author<input aria-label="Author" value={author} onChange={(event) => setAuthor(event.target.value)} maxLength="100" /></label>
        <label>Comment<textarea aria-label="Comment" value={text} onChange={(event) => setText(event.target.value)} maxLength="500" /></label>
        {error && <p className="error">{error}</p>}
        <button type="submit">Post comment</button>
      </form>
    </section>
  )
}