import api from './api'

export async function getCommentCount(taskId) {
  const { data } = await api.get(`/api/tasks/${taskId}/comments/count`)
  return data.count
}

export async function listComments(taskId) {
  const { data } = await api.get(`/api/tasks/${taskId}/comments`)
  return data
}

export async function createComment(taskId, comment) {
  const { data } = await api.post(`/api/tasks/${taskId}/comments`, comment)
  return data
}

export async function deleteComment(taskId, commentId) {
  await api.delete(`/api/tasks/${taskId}/comments/${commentId}`)
}