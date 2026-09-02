import { STATUSES, STATUS_LABELS } from '../constants'
import TaskCard from './TaskCard'

// Renders the three Kanban columns. When a status filter is active, only the
// matching column is shown.
export default function TaskList({ tasks, filter, commentCounts, commentsByTask, expandedTaskId, onAdvance, onDelete, onToggleComments, onCreateComment, onDeleteComment }) {
  const columns = filter === 'all' ? STATUSES : [filter]

  return (
    <div className="board">
      {columns.map((status) => {
        const columnTasks = tasks.filter((t) => t.status === status)
        return (
          <section className="column" key={status} aria-label={STATUS_LABELS[status]}>
            <h2>
              {STATUS_LABELS[status]} ({columnTasks.length})
            </h2>
            {columnTasks.length === 0 && <p className="assignee">No tasks</p>}
            {columnTasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                commentCount={commentCounts[task.id] || 0}
                comments={commentsByTask[task.id] || []}
                commentsOpen={expandedTaskId === task.id}
                onAdvance={onAdvance}
                onDelete={onDelete}
                onToggleComments={onToggleComments}
                onCreateComment={(comment) => onCreateComment(task.id, comment)}
                onDeleteComment={(commentId) => onDeleteComment(task.id, commentId)}
              />
            ))}
          </section>
        )
      })}
    </div>
  )
}
