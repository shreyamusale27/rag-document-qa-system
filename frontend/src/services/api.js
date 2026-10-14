import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

// ─── Documents ────────────────────────────────────────────────

export const uploadDocument = (file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)

  return api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event) => {
      if (onProgress && event.total) {
        onProgress(Math.round((event.loaded * 100) / event.total))
      }
    },
  })
}

export const listDocuments = () => api.get('/documents/')

export const getDocument = (docId) => api.get(`/documents/${docId}`)

export const deleteDocument = (docId) => api.delete(`/documents/${docId}`)

// ─── Q&A ──────────────────────────────────────────────────────

export const askQuestion = (question, documentIds = null, maxSources = 5) =>
  api.post('/qa/ask', {
    question,
    document_ids: documentIds && documentIds.length > 0 ? documentIds : null,
    max_sources: maxSources,
  })

export const getQAHealth = () => api.get('/qa/health')

export default api
