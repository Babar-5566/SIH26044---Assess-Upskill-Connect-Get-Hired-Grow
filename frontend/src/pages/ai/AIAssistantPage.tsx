/**
 * Enterprise Multi-LLM + Grounded RAG Assistant Corporate Dashboard
 * Skills: agency-ui-designer, agency-ux-architect, agency-frontend-developer
 */

import React, { useState, useEffect, useRef } from 'react'
import {
  Sparkles,
  Layers,
  MessageSquare,
  FileText,
  UploadCloud,
  Trash2,
  Send,
  RefreshCw,
  Clock,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  ChevronRight,
  ChevronDown,
  ShieldCheck,
  Bot,
  Eye,
  X,
} from 'lucide-react'
import {
  aiAssistantApi,
  LLMModelResult,
  RAGQueryResult,
  DocumentItem,
  DocumentDetail,
  CitationSource,
} from '../../api/aiAssistantApi'

export default function AIAssistantPage() {
  const [activeTab, setActiveTab] = useState<'arena' | 'chat' | 'rag'>('arena')

  // Multi-LLM Arena state
  const [arenaPrompt, setArenaPrompt] = useState('')
  const [arenaLoading, setArenaLoading] = useState(false)
  const [arenaResults, setArenaResults] = useState<LLMModelResult[]>([])
  const [arenaError, setArenaError] = useState<string | null>(null)

  // Single Model Chat state
  const [selectedProvider, setSelectedProvider] = useState('gemini')
  const [chatMessages, setChatMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([])
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)

  // RAG state
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [selectedDocId, setSelectedDocId] = useState<string>('')
  const [ragQuery, setRagQuery] = useState('')
  const [ragLoading, setRagLoading] = useState(false)
  const [ragResult, setRagResult] = useState<RAGQueryResult | null>(null)
  const [ragProvider, setRagProvider] = useState('gemini')
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [selectedCitation, setSelectedCitation] = useState<CitationSource | null>(null)
  const [inspectingDoc, setInspectingDoc] = useState<DocumentDetail | null>(null)
  const [inspectLoading, setInspectLoading] = useState(false)
  const [docToDelete, setDocToDelete] = useState<DocumentItem | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const [isDocListOpen, setIsDocListOpen] = useState(true)
  const [isDragOverQuery, setIsDragOverQuery] = useState(false)
  const [activeModels, setActiveModels] = useState<Record<string, string>>({
    openai: 'gpt-4o',
    claude: 'claude-3-5-sonnet',
    gemini: 'gemini-3-flash-preview',
  })

  useEffect(() => {
    fetchDocuments()
    fetchModels()
  }, [])

  const fetchModels = async () => {
    try {
      const res = await aiAssistantApi.getModels()
      if (res.data?.success) {
        const map: Record<string, string> = {}
        res.data.data.forEach((m: any) => {
          map[m.provider] = m.model
        })
        setActiveModels((prev) => ({ ...prev, ...map }))
      }
    } catch (err) {
      console.error('Failed to fetch models:', err)
    }
  }


  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  const fetchDocuments = async () => {
    try {
      const res = await aiAssistantApi.listDocuments()
      if (res.data?.success) {
        setDocuments(res.data.data)
      }
    } catch (err) {
      console.error('Failed to load documents:', err)
    }
  }

  // Handle Multi-LLM Comparison
  const handleCompare = async () => {
    if (!arenaPrompt.trim()) return
    setArenaLoading(true)
    setArenaError(null)
    try {
      const res = await aiAssistantApi.compareModels(arenaPrompt)
      if (res.data?.success) {
        setArenaResults(res.data.data)
      }
    } catch (err: any) {
      setArenaError(err.response?.data?.message || err.message || 'Comparison request failed')
    } finally {
      setArenaLoading(false)
    }
  }

  // Continue with selected model into single chat mode
  const handleContinueWithModel = (provider: string, initialResponse: string) => {
    setSelectedProvider(provider)
    setChatMessages([
      { role: 'user', content: arenaPrompt },
      { role: 'assistant', content: initialResponse },
    ])
    setActiveTab('chat')
  }

  // Handle Single Model Chat Send
  const handleChatSend = async () => {
    if (!chatInput.trim() || chatLoading) return
    const userMsg = chatInput.trim()
    const updatedHistory = [...chatMessages, { role: 'user' as const, content: userMsg }]
    setChatMessages(updatedHistory)
    setChatInput('')
    setChatLoading(true)

    try {
      const res = await aiAssistantApi.chatSingle(userMsg, selectedProvider, chatMessages)
      if (res.data?.success) {
        const reply = res.data.data.content || res.data.data.error_message || 'No response.'
        setChatMessages([...updatedHistory, { role: 'assistant', content: reply }])
      }
    } catch (err: any) {
      const errMsg = err.response?.data?.message || err.message || 'Failed to send message.'
      setChatMessages([...updatedHistory, { role: 'assistant', content: `⚠️ Error: ${errMsg}` }])
    } finally {
      setChatLoading(false)
    }
  }

  // Handle Document Upload
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setUploadError(null)
    try {
      const res = await aiAssistantApi.uploadDocument(file)
      if (res.data?.success) {
        await fetchDocuments()
        e.target.value = ''
      }
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || err.message || 'File upload failed')
    } finally {
      setUploading(false)
    }
  }

  // Handle Document Delete with In-App Animated Confirmation Modal
  const handleConfirmDelete = async () => {
    if (!docToDelete) return
    setIsDeleting(true)
    setDeleteError(null)
    try {
      await aiAssistantApi.deleteDocument(docToDelete.id)
      await fetchDocuments()
      if (selectedDocId === docToDelete.id) setSelectedDocId('')
      setDocToDelete(null)
    } catch (err: any) {
      setDeleteError(err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to delete document from vector index.')
    } finally {
      setIsDeleting(false)
    }
  }

  // Handle Document Inspection with Instant Feedback
  const handleInspectDoc = async (doc: DocumentItem) => {
    // Instant open (0ms latency): populate modal immediately with known doc metadata
    setInspectingDoc({
      ...doc,
      chunks: [],
    })
    setInspectLoading(true)
    try {
      const res = await aiAssistantApi.getDocument(doc.id)
      if (res.data?.success) {
        setInspectingDoc(res.data.data)
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to inspect document chunks.')
      setInspectingDoc(null)
    } finally {
      setInspectLoading(false)
    }
  }

  // Selected document helper
  const selectedDoc = documents.find((d) => d.id === selectedDocId)

  // Handle RAG Search (supports direct query, prompt override, and target docId)
  const handleRAGQuery = async (overridePrompt?: string, overrideDocId?: string) => {
    const queryToRun = (overridePrompt ?? ragQuery).trim()
    const targetDocId = overrideDocId !== undefined ? overrideDocId : selectedDocId
    if (!queryToRun || ragLoading) return
    if (overridePrompt) setRagQuery(overridePrompt)
    if (overrideDocId !== undefined) setSelectedDocId(overrideDocId)
    setRagLoading(true)
    setSelectedCitation(null)
    try {
      const res = await aiAssistantApi.queryRAG(queryToRun, ragProvider, targetDocId || undefined)
      if (res.data?.success) {
        setRagResult(res.data.data)
      }
    } catch (err: any) {
      alert(err.response?.data?.message || err.message || 'RAG Query failed')
    } finally {
      setRagLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-blue-950 text-white rounded-2xl p-5 md:p-6 shadow-xs border border-slate-800/80 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="p-2 bg-blue-500/10 text-blue-400 rounded-xl border border-blue-400/20">
              <Sparkles size={20} />
            </span>
            <h1 className="text-xl md:text-2xl font-bold tracking-tight text-white">Enterprise Multi-LLM + RAG Assistant</h1>
          </div>
          <p className="text-slate-300 text-xs md:text-sm mt-1.5 font-normal">
            Compare OpenAI, Claude, and Gemini side-by-side or query corporate documents with verifiable citations.
          </p>
        </div>
        <div className="flex items-center gap-2 bg-emerald-500/10 backdrop-blur-md px-3.5 py-1.5 rounded-full border border-emerald-500/20 text-xs text-emerald-300 font-medium">
          <ShieldCheck size={14} className="text-emerald-400" />
          <span>Strict Anti-Hallucination Active</span>
        </div>
      </div>

      {/* Navigation Tabs (Segmented Control) */}
      <div className="flex items-center">
        <div className="bg-gray-100/90 p-1 rounded-xl inline-flex items-center gap-1 border border-gray-200/80">
          <button
            onClick={() => setActiveTab('arena')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-xs md:text-sm transition-all ${
              activeTab === 'arena'
                ? 'bg-white text-gray-900 shadow-xs'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200/50'
            }`}
          >
            <Layers size={16} />
            Multi-LLM Arena
          </button>
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-xs md:text-sm transition-all ${
              activeTab === 'chat'
                ? 'bg-white text-gray-900 shadow-xs'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200/50'
            }`}
          >
            <MessageSquare size={16} />
            Continuous Chat
          </button>
          <button
            onClick={() => setActiveTab('rag')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-xs md:text-sm transition-all ${
              activeTab === 'rag'
                ? 'bg-white text-gray-900 shadow-xs'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200/50'
            }`}
          >
            <FileText size={16} />
            Document RAG & Citations
          </button>
        </div>
      </div>

      {/* TAB 1: MULTI-LLM ARENA */}
      {activeTab === 'arena' && (
        <div className="space-y-6">
          <div className="bg-white rounded-2xl p-5 md:p-6 border border-gray-200/80 shadow-xs space-y-4">
            <label className="block text-sm font-semibold text-gray-800">
              Ask a question to query OpenAI ({activeModels.openai}), Claude ({activeModels.claude}), and Gemini ({activeModels.gemini}) simultaneously:
            </label>
            <div className="flex gap-3">
              <textarea
                value={arenaPrompt}
                onChange={(e) => setArenaPrompt(e.target.value)}
                placeholder="e.g. Compare microservices vs monolithic architecture for high-concurrency systems..."
                rows={3}
                className="flex-1 border border-gray-200 rounded-xl p-3.5 text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none resize-none transition-all placeholder:text-gray-400"
              />
            </div>
            <div className="flex justify-end">
              <button
                onClick={handleCompare}
                disabled={arenaLoading || !arenaPrompt.trim()}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-5 py-2.5 rounded-xl font-medium text-sm shadow-xs hover:shadow-sm transition-all"
              >
                {arenaLoading ? (
                  <>
                    <RefreshCw size={15} className="animate-spin" />
                    Querying 3 Models in Parallel...
                  </>
                ) : (
                  <>
                    <Sparkles size={15} />
                    Compare Models Side-by-Side
                  </>
                )}
              </button>
            </div>
            {arenaError && (
              <div className="p-3 bg-red-50 text-red-700 text-xs md:text-sm rounded-xl border border-red-200 flex items-center gap-2">
                <AlertCircle size={16} />
                <span>{arenaError}</span>
              </div>
            )}
          </div>

          {/* Side-by-Side Arena Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {['openai', 'claude', 'gemini'].map((providerKey) => {
              const res = arenaResults.find((r) => r.provider.toLowerCase() === providerKey)
              const badgeColors: Record<string, { title: string; badge: string; border: string }> = {
                openai: { title: `OpenAI (${activeModels.openai})`, badge: 'bg-emerald-50 text-emerald-800 border-emerald-200', border: 'border-gray-200/80 hover:border-emerald-300' },
                claude: { title: `Anthropic (${activeModels.claude})`, badge: 'bg-purple-50 text-purple-800 border-purple-200', border: 'border-gray-200/80 hover:border-purple-300' },
                gemini: { title: `Google Gemini (${activeModels.gemini})`, badge: 'bg-blue-50 text-blue-800 border-blue-200', border: 'border-gray-200/80 hover:border-blue-300' },
              }
              const meta = badgeColors[providerKey]

              return (
                <div
                  key={providerKey}
                  className={`bg-white rounded-2xl border ${meta.border} shadow-xs flex flex-col justify-between overflow-hidden transition-all hover:shadow-sm`}
                >
                  <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/60">
                    <div>
                      <h3 className="font-semibold text-gray-900 text-xs md:text-sm tracking-tight">{meta.title}</h3>
                      <p className="text-[11px] text-gray-400 mt-0.5">{res?.model || 'Model ready'}</p>
                    </div>
                    {res && (
                      <div className="flex items-center gap-2">
                        {res.status === 'SUCCESS' ? (
                          <span className="flex items-center gap-1 text-[11px] font-medium text-gray-600 bg-white px-2.5 py-1 rounded-full border border-gray-200 shadow-2xs">
                            <Clock size={12} className="text-blue-500" />
                            {res.latency_ms} ms
                          </span>
                        ) : (
                          <span className="text-[11px] font-medium text-red-600 bg-red-50 px-2 py-0.5 rounded-full border border-red-200">
                            Failed
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="p-4 md:p-5 flex-1 min-h-[260px] max-h-[420px] overflow-y-auto text-xs md:text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                    {arenaLoading ? (
                      <div className="h-full flex flex-col items-center justify-center text-gray-400 gap-3 py-12">
                        <RefreshCw size={22} className="animate-spin text-blue-500" />
                        <span className="text-xs">Generating response...</span>
                      </div>
                    ) : res ? (
                      res.status === 'SUCCESS' ? (
                        res.content
                      ) : (
                        <div className="p-3 bg-red-50 rounded-xl text-xs text-red-700 border border-red-100">
                          <strong>Provider Notice:</strong> {res.error_message || 'Service unavailable'}
                        </div>
                      )
                    ) : (
                      <div className="h-full flex flex-col items-center justify-center text-gray-400 py-12 text-center">
                        <Bot size={30} className="text-gray-300 mb-2" />
                        <span className="text-xs">Awaiting your question</span>
                      </div>
                    )}
                  </div>

                  {res?.status === 'SUCCESS' && (
                    <div className="p-3.5 border-t border-gray-100 bg-gray-50/50">
                      <button
                        onClick={() => handleContinueWithModel(res.provider, res.content)}
                        className="w-full flex items-center justify-center gap-1.5 bg-white hover:bg-blue-50 text-blue-700 border border-blue-200 hover:border-blue-300 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all shadow-2xs"
                      >
                        Continue with this model
                        <ChevronRight size={14} />
                      </button>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* TAB 2: CONTINUOUS CHAT */}
      {activeTab === 'chat' && (
        <div className="bg-white rounded-2xl border border-gray-200/80 shadow-xs flex flex-col h-[650px] overflow-hidden">
          {/* Chat Topbar */}
          <div className="p-3.5 md:p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/60">
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Active Model:</span>
              <select
                value={selectedProvider}
                onChange={(e) => setSelectedProvider(e.target.value)}
                className="border border-gray-200 rounded-xl px-3 py-1.5 text-xs font-medium text-gray-800 bg-white outline-none hover:border-gray-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-2xs"
              >
                <option value="gemini">Google Gemini ({activeModels.gemini})</option>
                <option value="openai">OpenAI ({activeModels.openai})</option>
                <option value="claude">Anthropic Claude ({activeModels.claude})</option>
              </select>
            </div>
            <button
              onClick={() => setChatMessages([])}
              className="text-xs font-medium text-gray-500 hover:text-red-600 transition-colors px-2.5 py-1 rounded-lg hover:bg-red-50/80"
            >
              Clear Conversation
            </button>
          </div>

          {/* Messages Thread */}
          <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
            {chatMessages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-400 text-center py-16">
                <MessageSquare size={34} className="text-gray-300 mb-2.5" />
                <p className="text-sm font-semibold text-gray-700">Start a conversation with {selectedProvider.toUpperCase()}</p>
                <p className="text-xs text-gray-400 mt-1">Multi-turn conversation history is preserved across turns.</p>
              </div>
            ) : (
              chatMessages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[78%] rounded-2xl px-4 py-3 text-xs md:text-sm leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white rounded-br-xs shadow-2xs'
                        : 'bg-gray-100/90 text-gray-800 rounded-bl-xs border border-gray-200/70 shadow-2xs'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))
            )}
            {chatLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100/80 rounded-2xl px-4 py-2.5 text-xs text-gray-600 flex items-center gap-2 border border-gray-200/60 shadow-2xs">
                  <RefreshCw size={13} className="animate-spin text-blue-600" />
                  <span>{selectedProvider} is thinking...</span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input Bar */}
          <div className="p-3.5 md:p-4 border-t border-gray-100 bg-white flex gap-2.5 items-center">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleChatSend()}
              placeholder={`Message ${selectedProvider}...`}
              className="flex-1 border border-gray-200 bg-gray-50/50 hover:bg-white focus:bg-white rounded-xl px-4 py-2.5 text-xs md:text-sm outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-2xs placeholder:text-gray-400"
            />
            <button
              onClick={handleChatSend}
              disabled={chatLoading || !chatInput.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white p-2.5 rounded-xl transition-all shadow-2xs hover:shadow-xs flex items-center justify-center"
            >
              <Send size={17} />
            </button>
          </div>
        </div>
      )}

      {/* TAB 3: DOCUMENT RAG & CITATIONS */}
      {activeTab === 'rag' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Document Ingestion Drawer */}
          <div className="lg:col-span-1 space-y-4">
            <div className="bg-white rounded-2xl p-5 border border-gray-200/80 shadow-xs space-y-4">
              <h3 className="font-semibold text-gray-900 text-sm flex items-center gap-2">
                <UploadCloud size={18} className="text-blue-600" />
                Document Ingestion
              </h3>
              <p className="text-xs text-gray-500">
                Upload PDF, DOCX, or TXT (up to 25MB). Chunks & vector embeddings are indexed automatically.
              </p>

              <label className="block w-full border-2 border-dashed border-gray-200 hover:border-blue-400 rounded-xl p-4 text-center cursor-pointer transition-all bg-gray-50/50 hover:bg-blue-50/40">
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  className="hidden"
                />
                {uploading ? (
                  <div className="flex items-center justify-center gap-2 text-xs text-blue-600">
                    <RefreshCw size={16} className="animate-spin" />
                    <span>Parsing & vectorizing...</span>
                  </div>
                ) : (
                  <div className="space-y-1">
                    <UploadCloud size={24} className="mx-auto text-gray-400" />
                    <p className="text-xs font-medium text-gray-700">Choose file or drag here</p>
                    <p className="text-[10px] text-gray-400">PDF, Word DOCX, Plain TXT</p>
                  </div>
                )}
              </label>

              {uploadError && (
                <div className="p-2.5 bg-red-50 text-red-700 text-xs rounded-xl border border-red-200 flex items-center gap-1.5">
                  <AlertCircle size={14} />
                  <span>{uploadError}</span>
                </div>
              )}

              {/* Uploaded Documents Collapsible List */}
              <div className="pt-2">
                <button
                  type="button"
                  onClick={() => setIsDocListOpen(!isDocListOpen)}
                  className="w-full flex items-center justify-between text-xs font-semibold text-gray-600 hover:text-gray-900 uppercase tracking-wider mb-2 py-1 select-none transition-colors group cursor-pointer"
                  title="Click to collapse or expand document list"
                >
                  <div className="flex items-center gap-2">
                    <span>Indexed Documents</span>
                    <span className="px-2 py-0.5 text-[10px] rounded-full bg-blue-100 text-blue-800 font-semibold lowercase">
                      {documents.length}
                    </span>
                  </div>
                  <div className="text-gray-400 group-hover:text-gray-700 transition-transform p-0.5 rounded hover:bg-gray-100">
                    {isDocListOpen ? <ChevronDown size={15} /> : <ChevronRight size={15} />}
                  </div>
                </button>

                {isDocListOpen && (
                  <div className="space-y-2 max-h-[300px] overflow-y-auto pr-0.5 transition-all">
                    {documents.length === 0 ? (
                      <p className="text-xs text-gray-400 italic">No documents uploaded yet.</p>
                    ) : (
                      documents.map((doc) => (
                        <div
                          key={doc.id}
                          draggable={true}
                          onDragStart={(e) => {
                            e.dataTransfer.setData('text/plain', doc.id)
                            e.dataTransfer.effectAllowed = 'copyMove'
                          }}
                          className={`p-3 rounded-xl border text-xs flex items-center justify-between transition-all select-none cursor-grab active:cursor-grabbing ${
                            selectedDocId === doc.id
                              ? 'bg-blue-50/90 border-blue-400 text-blue-950 shadow-2xs ring-1 ring-blue-400/50'
                              : 'bg-gray-50/60 border-gray-200/80 text-gray-800 hover:bg-gray-100/70 hover:border-gray-300'
                          }`}
                          title="Click to select or drag into query box to focus analysis"
                        >
                          <div
                            onClick={() => setSelectedDocId(selectedDocId === doc.id ? '' : doc.id)}
                            className="flex-1 cursor-pointer pr-2 overflow-hidden"
                          >
                            <p className="font-medium truncate">{doc.original_filename}</p>
                            <p className="text-[10px] text-gray-500">
                              {doc.file_type.toUpperCase()} • {doc.chunk_count} chunks
                            </p>
                          </div>
                          <div className="flex items-center gap-1">
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                const nextId = selectedDocId === doc.id ? '' : doc.id
                                setSelectedDocId(nextId)
                                if (nextId) {
                                  handleRAGQuery('Provide an executive summary and core key takeaways of this document.', nextId)
                                }
                              }}
                              className={`p-1.5 rounded-lg transition-all active:scale-90 flex items-center gap-1 text-[10px] font-medium ${
                                selectedDocId === doc.id
                                  ? 'bg-blue-600 text-white shadow-2xs'
                                  : 'text-blue-700 bg-blue-50 hover:bg-blue-100/80'
                              }`}
                              title="Focus and instantly re-analyze this document"
                            >
                              <Sparkles size={12} />
                              <span>{selectedDocId === doc.id ? 'Focused' : 'Analyze'}</span>
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                handleInspectDoc(doc)
                              }}
                              className="text-gray-400 hover:text-blue-600 transition-all p-1.5 rounded-lg hover:bg-blue-50 active:scale-90"
                              title="Open & inspect document chunks"
                            >
                              <Eye size={14} />
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                setDeleteError(null)
                                setDocToDelete(doc)
                              }}
                              className="text-gray-400 hover:text-red-600 transition-colors p-1.5 rounded-lg hover:bg-red-50 active:scale-90"
                              title="Remove document & vectors"
                            >
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* RAG Query & Grounded Answer Panel */}
          <div
            onDragOver={(e) => {
              e.preventDefault()
              e.dataTransfer.dropEffect = 'copy'
              if (!isDragOverQuery) setIsDragOverQuery(true)
            }}
            onDragLeave={() => setIsDragOverQuery(false)}
            onDrop={(e) => {
              e.preventDefault()
              setIsDragOverQuery(false)
              const droppedDocId = e.dataTransfer.getData('text/plain')
              if (droppedDocId) {
                setSelectedDocId(droppedDocId)
              }
            }}
            className={`lg:col-span-2 space-y-4 rounded-2xl transition-all ${
              isDragOverQuery ? 'ring-2 ring-blue-500 ring-offset-2' : ''
            }`}
          >
            <div className="bg-white rounded-2xl p-5 md:p-6 border border-gray-200/80 shadow-xs space-y-4">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-gray-900 text-sm">Ask Document Question</h3>
                  {isDragOverQuery && (
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full font-medium animate-pulse">
                      Drop document here to focus!
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">Synthesis Model:</span>
                  <select
                    value={ragProvider}
                    onChange={(e) => setRagProvider(e.target.value)}
                    className="border border-gray-200 rounded-xl px-2.5 py-1.5 text-xs text-gray-700 bg-white outline-none hover:border-gray-300 shadow-2xs"
                  >
                    <option value="gemini">Google Gemini ({activeModels.gemini})</option>
                    <option value="openai">OpenAI ({activeModels.openai})</option>
                    <option value="claude">Anthropic Claude ({activeModels.claude})</option>
                  </select>
                </div>
              </div>

              {/* Focused Document Active Banner with 1-Click Re-Analysis Shortcuts */}
              {selectedDoc && (
                <div className="p-3 bg-gradient-to-r from-blue-50 to-indigo-50/40 border border-blue-200/90 rounded-xl space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-blue-950 font-medium">
                      <FileText size={15} className="text-blue-600" />
                      <span>Focused Document for Analysis:</span>
                      <span className="bg-white px-2.5 py-0.5 rounded-lg border border-blue-200 font-semibold text-blue-800 shadow-2xs">
                        {selectedDoc.original_filename}
                      </span>
                      <span className="text-[10px] text-blue-600 bg-blue-100/80 px-2 py-0.5 rounded-full">
                        {selectedDoc.chunk_count} chunks
                      </span>
                    </div>
                    <button
                      onClick={() => setSelectedDocId('')}
                      className="text-blue-500 hover:text-blue-800 p-1 rounded-md hover:bg-blue-100 transition-colors flex items-center gap-1 text-[11px]"
                      title="Clear focus (query all documents)"
                    >
                      <X size={13} />
                      <span>Clear Focus</span>
                    </button>
                  </div>

                  <div className="flex items-center gap-1.5 flex-wrap pt-1">
                    <span className="text-[11px] text-blue-700 font-medium">1-Click Re-Analysis:</span>
                    <button
                      onClick={() =>
                        handleRAGQuery(
                          'Provide a comprehensive executive summary of this document, highlighting its core themes, key findings, and actionable conclusions.'
                        )
                      }
                      className="px-2.5 py-1 bg-white hover:bg-blue-600 hover:text-white text-blue-700 rounded-lg border border-blue-200 font-medium shadow-2xs transition-all active:scale-95 text-[11px]"
                    >
                      ⚡ Executive Summary
                    </button>
                    <button
                      onClick={() =>
                        handleRAGQuery(
                          'Extract the top key points, critical data, and core takeaways from this document.'
                        )
                      }
                      className="px-2.5 py-1 bg-white hover:bg-blue-600 hover:text-white text-blue-700 rounded-lg border border-blue-200 font-medium shadow-2xs transition-all active:scale-95 text-[11px]"
                    >
                      🔍 Key Highlights
                    </button>
                    <button
                      onClick={() =>
                        handleRAGQuery(
                          'What are the most critical questions and answers that can be derived directly from this document?'
                        )
                      }
                      className="px-2.5 py-1 bg-white hover:bg-blue-600 hover:text-blue-700 rounded-lg border border-blue-200 font-medium shadow-2xs transition-all active:scale-95 text-[11px]"
                    >
                      ❓ Core Q&A
                    </button>
                  </div>
                </div>
              )}

              <div className="flex gap-2">
                <input
                  type="text"
                  value={ragQuery}
                  onChange={(e) => setRagQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleRAGQuery()}
                  placeholder={
                    selectedDoc
                      ? `Ask anything specifically about "${selectedDoc.original_filename}"...`
                      : 'Ask a question across all uploaded documents (or drag a document here)...'
                  }
                  className="flex-1 border border-gray-200 bg-gray-50/50 hover:bg-white focus:bg-white rounded-xl px-4 py-2.5 text-xs md:text-sm outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 shadow-2xs transition-all placeholder:text-gray-400"
                />
                <button
                  onClick={() => handleRAGQuery()}
                  disabled={ragLoading || !ragQuery.trim()}
                  className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-5 py-2.5 rounded-xl text-xs md:text-sm font-medium flex items-center gap-2 shadow-2xs hover:shadow-xs transition-all"
                >
                  {ragLoading ? <RefreshCw size={15} className="animate-spin" /> : <Send size={15} />}
                  Query
                </button>
              </div>

              {/* RAG Answer Display */}
              {ragResult && (
                <div className="mt-6 space-y-4 border-t border-gray-100 pt-6">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                      Grounded Answer ({ragResult.model_used}):
                    </span>
                    <span className="text-xs text-gray-400">
                      ⚡ {ragResult.latency_ms}ms • {ragResult.retrieved_chunks_count} chunks retrieved
                    </span>
                  </div>

                  <div
                    className={`p-4 md:p-5 rounded-xl text-xs md:text-sm leading-relaxed whitespace-pre-wrap shadow-2xs ${
                      ragResult.status === 'INSUFFICIENT_INFO'
                        ? 'bg-amber-50/80 text-amber-900 border border-amber-200/80'
                        : 'bg-gray-50/70 text-gray-800 border border-gray-200/80'
                    }`}
                  >
                    {ragResult.answer}
                  </div>

                  {/* Clickable Citations Panel */}
                  {ragResult.sources && ragResult.sources.length > 0 && (
                    <div className="space-y-3">
                      <h4 className="text-xs font-semibold text-gray-700 flex items-center gap-1.5">
                        <CheckCircle2 size={14} className="text-emerald-600" />
                        Clickable Source Citations:
                      </h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {ragResult.sources.map((src) => (
                          <div
                            key={src.chunk_id}
                            onClick={() => setSelectedCitation(selectedCitation?.chunk_id === src.chunk_id ? null : src)}
                            className={`p-3.5 rounded-xl border text-xs cursor-pointer transition-all ${
                              selectedCitation?.chunk_id === src.chunk_id
                                ? 'bg-blue-50/90 border-blue-400 shadow-xs'
                                : 'bg-white border-gray-200/80 hover:border-blue-300 hover:shadow-2xs'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-semibold text-blue-700">
                                [{src.index}] {src.filename}
                              </span>
                              <span className="text-[10px] bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full font-medium">
                                {Math.round(src.similarity_score * 100)}% match
                              </span>
                            </div>
                            {src.page_number && (
                              <p className="text-[10px] text-gray-500 mt-1">Page {src.page_number}</p>
                            )}
                            <p className="text-gray-600 mt-2 line-clamp-2 italic">"{src.snippet}"</p>
                          </div>
                        ))}
                      </div>

                      {/* Expanded Citation Modal / Drawer */}
                      {selectedCitation && (
                        <div className="p-4 bg-blue-50/60 border border-blue-200/80 rounded-xl text-xs space-y-2.5 shadow-2xs">
                          <div className="flex justify-between items-center font-semibold text-blue-900">
                            <span>
                              Full Snippet — [{selectedCitation.index}] {selectedCitation.filename}
                              {selectedCitation.page_number ? ` (Page ${selectedCitation.page_number})` : ''}
                            </span>
                            <button
                              onClick={() => setSelectedCitation(null)}
                              className="text-gray-400 hover:text-gray-600 text-xs px-1.5 py-0.5 rounded hover:bg-blue-100/60"
                            >
                              ✕ Close
                            </button>
                          </div>
                          <p className="text-gray-700 whitespace-pre-wrap leading-relaxed bg-white p-3 rounded-lg border border-blue-100">
                            {selectedCitation.snippet}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      {/* Document Chunk Inspector Modal */}
      {inspectingDoc && (
        <div
          onClick={() => setInspectingDoc(null)}
          className="fixed inset-0 bg-black/50 transition-opacity duration-200 z-50 flex items-center justify-center p-4 sm:p-6"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="bg-white rounded-2xl max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl border border-gray-200/90 overflow-hidden transform transition-all duration-200"
          >
            {/* Modal Header */}
            <div className="p-4 md:p-5 border-b border-gray-100 flex items-center justify-between bg-gray-50/80">
              <div className="flex items-center gap-3 min-w-0">
                <span className="p-2.5 bg-blue-100 text-blue-700 rounded-xl shrink-0">
                  <FileText size={18} />
                </span>
                <div className="min-w-0">
                  <h3 className="font-semibold text-gray-900 text-sm md:text-base leading-tight truncate">
                    {inspectingDoc.original_filename}
                  </h3>
                  <p className="text-[11px] text-gray-500 mt-0.5">
                    {inspectingDoc.file_type.toUpperCase()} • {inspectingDoc.chunk_count} Vectorized Chunks
                    {inspectingDoc.file_size_bytes > 0 && ` • ${(inspectingDoc.file_size_bytes / 1024).toFixed(1)} KB`}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setInspectingDoc(null)}
                className="text-gray-400 hover:text-gray-600 p-1.5 rounded-lg hover:bg-gray-200/60 transition-colors shrink-0"
                title="Close"
              >
                <X size={18} />
              </button>
            </div>

            {/* Chunks List */}
            <div className="p-4 md:p-6 overflow-y-auto flex-1 space-y-3.5 bg-slate-50/50">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Extracted Document Chunks ({inspectLoading ? 'Loading...' : (inspectingDoc.chunks?.length || 0)})
                </span>
                <span className="text-[11px] text-gray-400">
                  Indexed with Dense Vector Embeddings
                </span>
              </div>

              {inspectLoading ? (
                /* Instant skeleton loader while chunks are fetching */
                <div className="space-y-3 py-1">
                  {[1, 2, 3].map((n) => (
                    <div
                      key={n}
                      className="bg-white rounded-xl p-4 border border-gray-100 shadow-2xs space-y-2.5 animate-pulse"
                    >
                      <div className="flex justify-between items-center pb-2 border-b border-gray-50">
                        <div className="h-3.5 w-24 bg-gray-200 rounded-md" />
                        <div className="h-3 w-16 bg-gray-100 rounded-md" />
                      </div>
                      <div className="space-y-2 pt-1">
                        <div className="h-2.5 bg-gray-100 rounded w-full" />
                        <div className="h-2.5 bg-gray-100 rounded w-5/6" />
                        <div className="h-2.5 bg-gray-100 rounded w-4/6" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (!inspectingDoc.chunks || inspectingDoc.chunks.length === 0) ? (
                <div className="p-10 text-center text-gray-400 text-xs">
                  No text chunks stored in the active vector index for this document.
                </div>
              ) : (
                inspectingDoc.chunks.map((chunk, idx) => (
                  <div
                    key={chunk.chunk_id || idx}
                    className="bg-white rounded-xl p-4 border border-gray-200/80 shadow-2xs space-y-2 hover:border-blue-200 transition-colors"
                  >
                    <div className="flex items-center justify-between text-xs border-b border-gray-100 pb-2">
                      <span className="font-semibold text-blue-700 flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-blue-500" />
                        Chunk #{chunk.chunk_index + 1}
                      </span>
                      <div className="flex items-center gap-2 text-gray-400 text-[11px]">
                        {chunk.page_number && <span>Page {chunk.page_number}</span>}
                        <span>•</span>
                        <span>{chunk.content.length} characters</span>
                      </div>
                    </div>
                    <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap font-sans">
                      {chunk.content}
                    </p>
                  </div>
                ))
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-gray-100 bg-white flex justify-between items-center">
              <span className="text-xs text-gray-400">
                Indexed in NumPy Vector Store
              </span>
              <button
                onClick={() => setInspectingDoc(null)}
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold px-4 py-2 rounded-xl text-xs transition-colors shadow-2xs hover:shadow-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Premium In-App Delete Confirmation Modal with Smooth Animation */}
      {docToDelete && (
        <div
          onClick={() => !isDeleting && setDocToDelete(null)}
          className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 transition-opacity animate-in fade-in duration-200"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="bg-white rounded-2xl shadow-2xl border border-red-100/90 max-w-md w-full p-6 space-y-5 transition-all transform animate-in zoom-in-95 duration-200"
          >
            {/* Header with Icon */}
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-2xl bg-red-50 border border-red-100 flex items-center justify-center text-red-600 shrink-0 shadow-2xs">
                <Trash2 size={24} />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-base font-bold text-gray-900 tracking-tight">
                  Delete Vectorized Document?
                </h3>
                <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                  Are you sure you want to delete this document from the vector index?
                </p>
              </div>
              <button
                onClick={() => !isDeleting && setDocToDelete(null)}
                disabled={isDeleting}
                className="text-gray-400 hover:text-gray-600 p-1.5 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50 shrink-0 cursor-pointer"
                title="Cancel and close"
              >
                <X size={18} />
              </button>
            </div>

            {/* Document Info Card */}
            <div className="p-3.5 bg-gray-50/90 rounded-xl border border-gray-200/70 space-y-1 text-xs">
              <div className="flex items-center gap-2 text-gray-900 font-semibold truncate">
                <FileText size={15} className="text-blue-600 shrink-0" />
                <span className="truncate">{docToDelete.original_filename}</span>
              </div>
              <div className="flex items-center gap-2 text-gray-500 text-[11px] pl-6">
                <span className="font-medium text-gray-600">{docToDelete.file_type.toUpperCase()}</span>
                <span>•</span>
                <span>{docToDelete.chunk_count} Vector Chunks</span>
                {docToDelete.file_size_bytes > 0 && (
                  <>
                    <span>•</span>
                    <span>{(docToDelete.file_size_bytes / 1024).toFixed(1)} KB</span>
                  </>
                )}
              </div>
            </div>

            {deleteError && (
              <div className="p-3 bg-red-50 text-red-700 text-xs rounded-xl border border-red-200 flex items-center gap-2">
                <AlertCircle size={14} className="shrink-0" />
                <span>{deleteError}</span>
              </div>
            )}

            <div className="p-3 bg-red-50/60 rounded-xl border border-red-100 text-xs text-red-800 space-y-1 leading-relaxed">
              <p className="font-semibold flex items-center gap-1.5 text-red-900">
                <AlertCircle size={13} className="text-red-600" />
                Permanent Vector Purge
              </p>
              <p className="text-[11px] text-red-700">
                All associated embeddings and chunks will be removed. Any ongoing queries referencing this document will immediately lose this context.
              </p>
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-gray-100">
              <button
                type="button"
                onClick={() => setDocToDelete(null)}
                disabled={isDeleting}
                className="px-4 py-2.5 rounded-xl border border-gray-200 bg-white hover:bg-gray-50 text-gray-700 text-xs md:text-sm font-medium transition-all active:scale-95 disabled:opacity-50 shadow-2xs cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmDelete}
                disabled={isDeleting}
                className="px-5 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 active:scale-95 text-white text-xs md:text-sm font-medium shadow-xs hover:shadow-sm transition-all flex items-center gap-2 disabled:opacity-60 cursor-pointer"
              >
                {isDeleting ? (
                  <>
                    <RefreshCw size={14} className="animate-spin" />
                    <span>Purging Vectors...</span>
                  </>
                ) : (
                  <>
                    <Trash2 size={14} />
                    <span>Delete Document</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
