import api from './api'

// Thin wrapper over the /api/tasks endpoints. Keeping HTTP details in one
// module means components never import axios directly — which also makes them
// trivial to test with a mocked service.

export async function listTasks(status, deleted = false) {
  const params = {
    ...(status && status !== 'all' ? { status } : {}),
    ...(deleted ? { deleted: true } : {}),
  }
  const { data } = await api.get('/api/tasks', { params })
  return data
}

export async function getTask(id, includeDeleted = false) {
  const { data } = includeDeleted
    ? await api.get(`/api/tasks/${id}`, { params: { includeDeleted: true } })
    : await api.get(`/api/tasks/${id}`)
  return data
}

export async function createTask(task) {
  const { data } = await api.post('/api/tasks', task)
  return data
}

export async function updateTask(id, task) {
  const { data } = await api.put(`/api/tasks/${id}`, task)
  return data
}

export async function deleteTask(id) {
  await api.delete(`/api/tasks/${id}`)
}

export async function restoreTask(id) {
  await api.post(`/api/tasks/${id}/restore`)
}

export async function permanentlyDeleteTask(id) {
  await api.delete(`/api/tasks/${id}`, { params: { permanent: true } })
}
