import { useCallback, useEffect, useState } from 'react'
import StatusFilter from '../components/StatusFilter'
import TaskForm from '../components/TaskForm'
import TaskList from '../components/TaskList'
import * as commentService from '../services/commentService'
import * as taskService from '../services/taskService'

// Container component: owns the task list state and all data fetching.
export default function BoardPage() {
  const [tasks, setTasks] = useState([])
  const [filter, setFilter] = useState('all')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [commentCounts, setCommentCounts] = useState({})
  const [commentsByTask, setCommentsByTask] = useState({})
  const [expandedTaskId, setExpandedTaskId] = useState(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      // Filtering is done server-side; we pass the current filter through.
      const loadedTasks = await taskService.listTasks(filter)
      const counts = await Promise.all(loadedTasks.map(async (task) => [
        task.id,
        await commentService.getCommentCount(task.id),
      ]))
      setTasks(loadedTasks)
      setCommentCounts(Object.fromEntries(counts))
    } catch {
      setError('Could not load tasks. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }, [filter])

  useEffect(() => {
    refresh()
  }, [refresh])

  async function handleCreate(task) {
    await taskService.createTask(task)
    await refresh()
  }

  async function handleAdvance(task, nextStatus) {
    await taskService.updateTask(task.id, { ...task, status: nextStatus })
    await refresh()
  }

  async function handleDelete(task) {
    await taskService.deleteTask(task.id)
    await refresh()
  }

  async function loadComments(taskId) {
    const comments = await commentService.listComments(taskId)
    setCommentsByTask((current) => ({ ...current, [taskId]: comments }))
  }

  async function handleToggleComments(taskId) {
    if (expandedTaskId === taskId) {
      setExpandedTaskId(null)
      return
    }
    await loadComments(taskId)
    setExpandedTaskId(taskId)
  }

  async function handleCreateComment(taskId, comment) {
    await commentService.createComment(taskId, comment)
    await loadComments(taskId)
    setCommentCounts((current) => ({ ...current, [taskId]: (current[taskId] || 0) + 1 }))
  }

  async function handleDeleteComment(taskId, commentId) {
    await commentService.deleteComment(taskId, commentId)
    await loadComments(taskId)
    setCommentCounts((current) => ({ ...current, [taskId]: Math.max((current[taskId] || 0) - 1, 0) }))
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Engineering Task Board</h1>
        <span className="assignee">Module 01 — AI Champions Programme</span>
      </header>

      <TaskForm onCreate={handleCreate} />

      <div className="toolbar">
        <StatusFilter value={filter} onChange={setFilter} />
        <button onClick={refresh}>Refresh</button>
      </div>

      {error && <p className="error">{error}</p>}
      {loading ? <p>Loading…</p> : (
        <TaskList
          tasks={tasks}
          filter={filter}
          commentCounts={commentCounts}
          commentsByTask={commentsByTask}
          expandedTaskId={expandedTaskId}
          onAdvance={handleAdvance}
          onDelete={handleDelete}
          onToggleComments={handleToggleComments}
          onCreateComment={handleCreateComment}
          onDeleteComment={handleDeleteComment}
        />
      )}
    </div>
  )
}
