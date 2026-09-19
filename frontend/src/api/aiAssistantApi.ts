/**
 * AI Assistant API Client
 * Skills: agency-frontend-developer, agency-software-architect
 */

import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({ baseURL })

export function getAssistantError(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) return 'Cannot reach the server. Check your connection and try again.'
    if (error.response.status === 401) return 'Your session has expired. Please sign in again.'
    const body = error.response?.data
    const message = body?.error?.message || body?.detail || body?.message
    if (typeof message === 'string' && message !== 'Internal server error') return message
    if (error.response.status >= 500) return 'The server could not complete this request. Please try again.'
  }
  return error instanceof Error ? error.message : fallback
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  const organizationId = localStorage.getItem('organization_id')
  if (organizationId) config.headers['X-Organization-ID'] = organizationId
  return config
})

export interface LLMModelResult {
  provider: string
  model: string
  content: string
  latency_ms: number
  status: 'SUCCESS' | 'ERROR'
  error_message?: string
}

export interface ModelStatus {
  provider: string
  model: string
  is_configured: boolean
}

export interface CitationSource {
  index: number
  document_id: string
  filename: string
  page_number?: number
  chunk_id: string
  snippet: string
  similarity_score: number
}

export interface RAGQueryResult {
  query: string
  answer: string
  sources: CitationSource[]
  retrieved_chunks_count: number
  model_used: string
  latency_ms: number
  status: string
  error_message?: string
}

export interface DocumentItem {
  id: string
  original_filename: string
  file_type: string
  file_size_bytes: number
  chunk_count: number
  status: string
  created_at: string
}

export interface DocumentChunkDetail {
  chunk_id: string
  chunk_index: number
  filename: string
  page_number?: number
  content: string
  metadata?: Record<string, any>
}

export interface DocumentDetail extends DocumentItem {
  chunks: DocumentChunkDetail[]
}

export const aiAssistantApi = {
  checkHealth: () => api.get('/health', { timeout: 8000 }),
  getModels: () => api.get('/ai-assistant/models'),
  compareModels: (prompt: string, system_prompt?: string) =>
    api.post('/ai-assistant/compare', { prompt, system_prompt }),
  chatSingle: (prompt: string, provider: string, conversation_history: any[], system_prompt?: string) =>
    api.post('/ai-assistant/chat', { prompt, provider, conversation_history, system_prompt }),
  uploadDocument: (file: File, onProgress?: (percent: number) => void) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/ai-assistant/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (event.total) onProgress?.(Math.round(event.loaded * 100 / event.total))
      },
    })
  },
  listDocuments: () => api.get('/ai-assistant/documents'),
  getDocument: (id: string) => api.get(`/ai-assistant/documents/${id}`),
  deleteDocument: (id: string) => api.delete(`/ai-assistant/documents/${id}`),
  queryRAG: (question: string, provider: string = 'gemini', document_id?: string) =>
    api.post('/ai-assistant/rag/query', { question, provider, document_id }),
}
