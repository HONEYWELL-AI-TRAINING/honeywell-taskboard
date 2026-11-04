import { useCallback, useEffect, useState } from 'react'
import StatusFilter from '../components/StatusFilter'
import TaskForm from '../components/TaskForm'
import TaskList from '../components/TaskList'
import * as taskService from '../services/taskService'

// Container component: owns the task list state and all data fetching.
export default function BoardPage() {
  const [tasks, setTasks] = useState([])
  const [filter, setFilter] = useState('all')
  const [showDeleted, setShowDeleted] = useState(false)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      // Filtering is done server-side; we pass the current filter through.
      setTasks(await taskService.listTasks(filter, showDeleted))
    } catch {
      setError('Could not load tasks. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }, [filter, showDeleted])

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

  async function handleRestore(task) {
    await taskService.restoreTask(task.id)
    await refresh()
  }

  async function handlePermanentDelete(task) {
    const confirmed = window.confirm(
      `Permanently delete "${task.title}"? This cannot be undone.`,
    )
    if (!confirmed) return

    await taskService.permanentlyDeleteTask(task.id)
    await refresh()
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Engineering Task Board</h1>
        <span className="assignee">Module 01 — AI Champions Programme</span>
      </header>

      {!showDeleted && <TaskForm onCreate={handleCreate} />}

      <div className="toolbar">
        <StatusFilter value={filter} onChange={setFilter} />
        <button onClick={refresh}>Refresh</button>
        <button onClick={() => setShowDeleted((value) => !value)}>
          {showDeleted ? 'Back to active tasks' : 'View deleted tasks'}
        </button>
      </div>

      {error && <p className="error">{error}</p>}
      {loading ? <p>Loading…</p> : (
        <TaskList
          tasks={tasks}
          filter={filter}
          onAdvance={handleAdvance}
          onDelete={handleDelete}
          deleted={showDeleted}
          onRestore={handleRestore}
          onPermanentlyDelete={handlePermanentDelete}
        />
      )}
    </div>
  )
}
