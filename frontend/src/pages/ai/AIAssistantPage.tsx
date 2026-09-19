import React, { useEffect, useRef, useState } from 'react'
import { ArrowRight, ArrowUp, BookOpen, Check, CheckCircle2, ChevronRight, Clock3, FileText, Layers3, Loader2, MessageSquare, Plus, Search, ShieldCheck, Sparkles, Trash2, UploadCloud, Wifi, WifiOff, X } from 'lucide-react'
import { aiAssistantApi, getAssistantError, type CitationSource, type DocumentDetail, type DocumentItem, type LLMModelResult, type ModelStatus, type RAGQueryResult } from '../../api/aiAssistantApi'
import { Answer, CopyButton, Dialog, EmptyState, LoadingAnswer, Notice, PROVIDERS, PROVIDER_IDS, ProviderMark, type Provider } from '../../components/ai/AssistantUI'
import './assistant.css'

type Tab = 'arena' | 'chat' | 'rag'
type Message = { role: 'user' | 'assistant'; content: string }
const EXAMPLES = [
  { label: 'Explore an idea', prompt: 'Compare microservices and monolithic architecture for a growing startup. Explain the trade-offs clearly.' },
  { label: 'Build a learning plan', prompt: 'Create a practical four-week learning plan for a Python developer getting started with AI engineering.' },
  { label: 'Make a decision', prompt: 'What should a small team consider when choosing between PostgreSQL and MongoDB?' },
]
const DOCUMENT_PROMPTS = [
  { label: 'Summarize', prompt: 'Summarize the main ideas and important conclusions in the selected document.' },
  { label: 'Key takeaways', prompt: 'What are the key facts and actionable takeaways in this document?' },
  { label: 'Requirements', prompt: 'List the requirements explicitly stated in this document, with sources.' },
]
const sizeLabel = (bytes: number) => bytes >= 1024 * 1024 ? `${(bytes / 1024 / 1024).toFixed(1)} MB` : `${Math.max(1, Math.round(bytes / 1024))} KB`

export default function AIAssistantPage() {
  const [tab, setTab] = useState<Tab>('arena')
  const [connection, setConnection] = useState<'checking' | 'online' | 'offline'>('checking')
  const [models, setModels] = useState<ModelStatus[]>([])
  const [prompt, setPrompt] = useState('')
  const [comparedPrompt, setComparedPrompt] = useState('')
  const [results, setResults] = useState<LLMModelResult[]>([])
  const [comparing, setComparing] = useState(false)
  const [compareError, setCompareError] = useState('')
  const [provider, setProvider] = useState<Provider>('gemini')
  const [histories, setHistories] = useState<Partial<Record<Provider, Message[]>>>({})
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [chatError, setChatError] = useState('')
  const messages = histories[provider] || []
  const chatScroll = useRef<HTMLDivElement>(null)
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [documentsLoading, setDocumentsLoading] = useState(true)
  const [documentsError, setDocumentsError] = useState('')
  const [documentSearch, setDocumentSearch] = useState('')
  const [selectedId, setSelectedId] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadError, setUploadError] = useState('')
  const [uploadName, setUploadName] = useState('')
  const [uploadSuccess, setUploadSuccess] = useState('')
  const [dragging, setDragging] = useState(false)
  const uploadLock = useRef(false)
  const fileInput = useRef<HTMLInputElement>(null)
  const [ragProvider, setRagProvider] = useState<Provider>('gemini')
  const [question, setQuestion] = useState('')
  const [ragLoading, setRagLoading] = useState(false)
  const [ragError, setRagError] = useState('')
  const [ragResult, setRagResult] = useState<RAGQueryResult | null>(null)
  const [citation, setCitation] = useState<CitationSource | null>(null)
  const [inspecting, setInspecting] = useState<DocumentDetail | null>(null)
  const [inspectLoading, setInspectLoading] = useState(false)
  const [inspectError, setInspectError] = useState('')
  const inspectRequest = useRef(0)
  const [deleting, setDeleting] = useState<DocumentItem | null>(null)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [deleteError, setDeleteError] = useState('')
  const selectedDocument = documents.find(document => document.id === selectedId)
  const visibleDocuments = documents.filter(document => document.original_filename.toLowerCase().includes(documentSearch.toLowerCase()))
  const busy = comparing || chatLoading || ragLoading

  async function loadDocuments() {
    setDocumentsLoading(true)
    setDocumentsError('')
    try {
      const response = await aiAssistantApi.listDocuments()
      if (!response.data?.success) throw new Error('Could not load your documents.')
      setDocuments(response.data.data)
    } catch (error) { setDocumentsError(getAssistantError(error, 'Could not load your documents.')) }
    finally { setDocumentsLoading(false) }
  }

  async function checkConnection() {
    setConnection('checking')
    try { await aiAssistantApi.checkHealth(); setConnection('online') }
    catch { setConnection('offline') }
  }

  async function refreshWorkspace() {
    await Promise.allSettled([
      checkConnection(),
      loadDocuments(),
      aiAssistantApi.getModels().then(response => {
        if (response.data?.success) setModels(response.data.data)
      }),
    ])
  }

  useEffect(() => { void refreshWorkspace() }, [])
  useEffect(() => {
    if (tab === 'chat') chatScroll.current?.scrollTo({ top: chatScroll.current.scrollHeight, behavior: 'smooth' })
  }, [histories, chatLoading, tab, provider])

  function modelName(id: Provider) { return models.find(model => model.provider === id)?.model || 'Model configuration' }
  function modelStatus(id: Provider) {
    const model = models.find(item => item.provider === id)
    return model ? model.is_configured ? 'Configured' : 'Not configured' : 'Status unavailable'
  }

  async function compare() {
    if (!prompt.trim() || comparing) return
    const submitted = prompt.trim()
    setComparing(true); setCompareError('')
    try {
      const response = await aiAssistantApi.compareModels(submitted)
      if (!response.data?.success) throw new Error('Comparison could not be completed.')
      setResults(response.data.data); setComparedPrompt(submitted)
    } catch (error) { setCompareError(getAssistantError(error, 'Comparison could not be completed.')) }
    finally { setComparing(false) }
  }

  function continueWith(id: Provider, answer: string) {
    if (chatLoading || comparing) return
    setProvider(id)
    setHistories(previous => ({ ...previous, [id]: [{ role: 'user', content: comparedPrompt }, { role: 'assistant', content: answer }] }))
    setChatError(''); setChatInput(''); setTab('chat')
  }

  function clearChat() {
    if (chatLoading) return
    setHistories(previous => ({ ...previous, [provider]: [] }))
    setChatError(''); setChatInput('')
  }

  async function sendChat() {
    if (!chatInput.trim() || chatLoading) return
    const userText = chatInput.trim()
    const history = histories[provider] || []
    const updated: Message[] = [...history, { role: 'user', content: userText }]
    setHistories(previous => ({ ...previous, [provider]: updated }))
    setChatInput(''); setChatError(''); setChatLoading(true)
    try {
      const response = await aiAssistantApi.chatSingle(userText, provider, history.slice(-100))
      const reply = response.data?.data
      if (!response.data?.success || reply?.status !== 'SUCCESS' || !reply.content?.trim()) throw new Error(reply?.error_message || 'No answer was returned. Please try again.')
      setHistories(previous => ({ ...previous, [provider]: [...updated, { role: 'assistant', content: reply.content }] }))
    } catch (error) {
      setChatError(getAssistantError(error, 'Could not send your message.'))
      setHistories(previous => ({ ...previous, [provider]: history })); setChatInput(userText)
    } finally { setChatLoading(false) }
  }

  async function upload(file: File) {
    if (uploadLock.current) return
    setUploadError(''); setUploadSuccess('')
    if (!/\.(pdf|docx|txt)$/i.test(file.name)) { setUploadError('Choose a PDF, Word document (.docx), or text file (.txt).'); return }
    if (file.size > 25 * 1024 * 1024) { setUploadError('This file is too large. Choose a file under 25 MB.'); return }
    if (!file.size) { setUploadError('This file is empty. Choose a document containing text.'); return }
    uploadLock.current = true
    setUploading(true); setUploadName(file.name); setUploadProgress(0)
    try {
      const response = await aiAssistantApi.uploadDocument(file, setUploadProgress)
      if (!response.data?.success) throw new Error('Your document could not be uploaded.')
      await loadDocuments()
      setSelectedId(response.data.data.document_id)
      setUploadSuccess(`${file.name} is ready to explore.`)
      setRagResult(null)
    } catch (error) { setUploadError(getAssistantError(error, 'Your document could not be uploaded.')) }
    finally { setUploading(false); uploadLock.current = false; if (fileInput.current) fileInput.current.value = '' }
  }

  async function askDocument(override?: string, documentId?: string) {
    const submitted = (override || question).trim()
    if (!submitted || ragLoading) return
    const target = documentId ?? selectedId
    if (override) setQuestion(override)
    if (documentId) setSelectedId(documentId)
    setRagLoading(true); setRagError(''); setRagResult(null); setCitation(null)
    try {
      const response = await aiAssistantApi.queryRAG(submitted, ragProvider, target || undefined)
      if (!response.data?.success || response.data.data.status === 'ERROR') throw new Error(response.data?.data?.error_message || 'Could not answer your question.')
      setRagResult(response.data.data)
    } catch (error) { setRagError(getAssistantError(error, 'Could not answer your question.')) }
    finally { setRagLoading(false) }
  }

  async function inspectDocument(document: DocumentItem) {
    const request = ++inspectRequest.current
    setInspecting({ ...document, chunks: [] }); setInspectLoading(true); setInspectError('')
    try {
      const response = await aiAssistantApi.getDocument(document.id)
      if (request === inspectRequest.current) setInspecting(response.data.data)
    } catch (error) { if (request === inspectRequest.current) setInspectError(getAssistantError(error, 'Could not open this document.')) }
    finally { if (request === inspectRequest.current) setInspectLoading(false) }
  }

  async function deleteDocument() {
    if (!deleting || deleteLoading) return
    setDeleteLoading(true); setDeleteError('')
    try {
      await aiAssistantApi.deleteDocument(deleting.id)
      setDocuments(previous => previous.filter(document => document.id !== deleting.id))
      if (selectedId === deleting.id) setSelectedId('')
      if (ragResult?.sources.some(source => source.document_id === deleting.id)) { setRagResult(null); setCitation(null) }
      setDeleting(null)
    } catch (error) { setDeleteError(getAssistantError(error, 'Could not delete this document.')) }
    finally { setDeleteLoading(false) }
  }

  function submitShortcut(event: React.KeyboardEvent<HTMLTextAreaElement>, action: () => void, enter = false) {
    if (event.nativeEvent.isComposing) return
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey || (enter && !event.shiftKey))) { event.preventDefault(); action() }
  }

  return <div className="ai-workspace">
    <header className="ai-page-header">
      <div><div className="ai-eyebrow"><span className="ai-brand-icon"><Sparkles size={14} /></span> INTELLIGENCE WORKSPACE</div>
        <h1>Multi-LLM &amp; RAG Assistant<span className="ai-title-dot">.</span></h1>
        <p>A fresh perspective. A clearer answer. Your knowledge, connected.</p>
      </div>
      <div className="ai-header-actions">
        <button type="button" className={`ai-connection ${connection}`} onClick={() => void refreshWorkspace()} disabled={connection === 'checking'} title="Check server connection">
          {connection === 'checking' ? <Loader2 size={13} className="ai-spin" /> : connection === 'online' ? <Wifi size={13} /> : <WifiOff size={13} />}
          {connection === 'checking' ? 'Connecting' : connection === 'online' ? 'Server connected' : 'Reconnect'}
        </button>
        <button type="button" className="ai-button secondary" disabled={busy} onClick={() => { clearChat(); setTab('chat') }}><Plus size={16} /> New chat</button>
      </div>
    </header>

    {connection === 'offline' && <Notice onRetry={() => void refreshWorkspace()}>Your workspace cannot reach the server. Reconnect to load documents and send questions.</Notice>}

    <nav className="ai-tabs" aria-label="Assistant workspace">
      {([
        { id: 'arena', label: 'Multi-LLM Arena', subtitle: 'Compare perspectives', icon: Layers3 },
        { id: 'chat', label: 'Continuous Chat', subtitle: 'Keep the conversation going', icon: MessageSquare },
        { id: 'rag', label: 'Document RAG & Citations', subtitle: 'Answers from your sources', icon: BookOpen },
      ] as const).map(item => <button type="button" key={item.id} aria-label={item.label} aria-pressed={tab === item.id} className={`ai-tab ${tab === item.id ? 'active' : ''}`} onClick={() => setTab(item.id)}>
        <item.icon size={19} /><span><strong>{item.label}</strong><small>{item.subtitle}</small></span><ChevronRight size={15} className="ai-tab-arrow" />
      </button>)}
    </nav>

    {tab === 'arena' && <section className="ai-section ai-enter">
      <div className="ai-section-intro"><div><span className="ai-eyebrow">ONE QUESTION. THREE PERSPECTIVES.</span><h2>Good questions deserve a second opinion.</h2><p>Ask once, compare the answers, then continue with the model that fits.</p></div><span className="ai-subtle-pill"><Layers3 size={14} /> 3 models · side by side</span></div>
      <div className="ai-composer">
        <label className="ai-sr-only" htmlFor="arena-question">Comparison question</label>
        <textarea id="arena-question" value={prompt} maxLength={10000} onChange={event => setPrompt(event.target.value)} onKeyDown={event => submitShortcut(event, () => void compare())} placeholder="What would you like a fresh perspective on?" rows={3} />
        <div className="ai-composer-footer"><div className="ai-model-stack" aria-label="OpenAI, Claude, Gemini">{PROVIDER_IDS.map(id => <ProviderMark key={id} provider={id} small />)}<span>OpenAI, Claude &amp; Gemini</span></div>
          <button type="button" className="ai-button primary" disabled={comparing || !prompt.trim()} aria-label="Compare Models Side-by-Side" onClick={() => void compare()}>{comparing ? <Loader2 size={16} className="ai-spin" /> : <Sparkles size={16} />}{comparing ? 'Comparing answers…' : 'Compare answers'}{!comparing && <ArrowRight size={16} />}</button>
        </div>
      </div>
      <div className="ai-suggestions"><span>Try a starting point</span>{EXAMPLES.map(example => <button type="button" key={example.label} disabled={comparing} onClick={() => setPrompt(example.prompt)}>{example.label}<ArrowUp size={12} /></button>)}<span className="ai-shortcut">Ctrl / ⌘ + Enter to send</span></div>
      {compareError && <Notice onRetry={() => void compare()}>{compareError}</Notice>}
      {results.length > 0 && !comparing && <div className="ai-results-heading"><span>THE COMPARISON</span><p>{comparedPrompt}</p></div>}
      <div className="ai-model-grid">
        {PROVIDER_IDS.map(id => {
          const result = results.find(item => item.provider === id)
          const success = result?.status === 'SUCCESS'
          return <article className={`ai-model-card ${PROVIDERS[id].color}`} key={id}>
            <div className="ai-model-heading"><ProviderMark provider={id} /><div><h3>{PROVIDERS[id].name}</h3><p title={result?.model || modelName(id)}>{result?.model || modelName(id)}</p></div><span className={`ai-status-dot ${success ? 'success' : result ? 'error' : ''}`} title={result ? result.status : modelStatus(id)} /></div>
            <div className="ai-model-content">{comparing ? <LoadingAnswer /> : result ? success ? <Answer text={result.content} /> : <div className="ai-provider-error"><span className="ai-soft-icon"><WifiOff size={22} /></span><h4>Unable to get an answer</h4><p>{result.error_message || 'Please try again in a moment.'}</p></div> : <div className="ai-card-empty"><span className="ai-card-line" /><span className="ai-card-line" /><span className="ai-card-line short" /><h4>A new perspective starts here</h4><p>{PROVIDERS[id].description}</p><span className="ai-status-label">{modelStatus(id)}</span></div>}</div>
            <div className="ai-model-meta"><span>{result && !comparing ? <><Clock3 size={13} />{(result.latency_ms / 1000).toFixed(1)}s response</> : 'Your answer will appear here'}</span>{success && !comparing && <CopyButton text={result.content} label={`Copy ${PROVIDERS[id].name} answer`} />}</div>
            <button type="button" className="ai-continue" disabled={!success || comparing || chatLoading} onClick={() => result && continueWith(id, result.content)}>Continue with {PROVIDERS[id].name}<ArrowRight size={15} /></button>
          </article>
        })}
      </div>
    </section>}

    {tab === 'chat' && <section className="ai-chat ai-panel ai-enter">
      <div className="ai-panel-heading"><div className="ai-heading-group"><ProviderMark provider={provider} small /><div><h2>Your conversation</h2><span>Each model keeps its own context in this session.</span></div></div><div className="ai-chat-controls"><select aria-label="Chat model" value={provider} disabled={chatLoading} onChange={event => { setProvider(event.target.value as Provider); setChatError('') }}>{PROVIDER_IDS.map(id => <option value={id} key={id}>{PROVIDERS[id].name}</option>)}</select><button type="button" className="ai-icon-button" aria-label="Clear Conversation" title="Clear conversation" disabled={chatLoading || !messages.length} onClick={clearChat}><Trash2 size={16} /></button></div></div>
      <div className="ai-chat-thread" ref={chatScroll} role="log" aria-live="polite" aria-label="Conversation">
        {!messages.length ? <div className="ai-chat-welcome"><EmptyState title={`Start a conversation with ${provider.toUpperCase()}`}>Bring an idea, ask a follow-up, or work through something together.</EmptyState><div className="ai-chat-starters">{['Explain a complex idea simply', 'Help me plan my next project', 'Review an approach with me'].map(text => <button type="button" key={text} onClick={() => setChatInput(text)}>{text}<ArrowRight size={14} /></button>)}</div></div> : messages.map((message, index) => <div className={`ai-message ${message.role}`} key={index}>
          <span className="ai-message-avatar">{message.role === 'assistant' ? <ProviderMark provider={provider} small /> : 'Y'}</span><div className="ai-message-main"><div className="ai-message-label">{message.role === 'user' ? 'You' : PROVIDERS[provider].name}{message.role === 'assistant' && <CopyButton text={message.content} />}</div><div className="ai-message-body">{message.role === 'assistant' ? <Answer text={message.content} /> : <p>{message.content}</p>}</div></div>
        </div>)}
        {chatLoading && <div className="ai-message assistant"><ProviderMark provider={provider} small /><LoadingAnswer label={`${PROVIDERS[provider].name} is thinking…`} /></div>}
      </div>
      <div className="ai-chat-bottom">{chatError && <Notice>{chatError}</Notice>}<div className="ai-chat-composer"><textarea value={chatInput} maxLength={10000} onChange={event => setChatInput(event.target.value)} onKeyDown={event => submitShortcut(event, () => void sendChat(), true)} placeholder={`Message ${provider}...`} aria-label="Your message" rows={2} /><button type="button" className="ai-send" aria-label="Send message" disabled={chatLoading || !chatInput.trim()} onClick={() => void sendChat()}>{chatLoading ? <Loader2 size={19} className="ai-spin" /> : <ArrowUp size={20} />}</button></div><p className="ai-composer-hint">Enter to send · Shift + Enter for a new line<span>AI can make mistakes. Review important information.</span></p></div>
    </section>}

    {tab === 'rag' && <section className="ai-rag-grid ai-enter">
      <aside className="ai-library ai-panel">
        <div className="ai-library-heading"><span className="ai-soft-icon"><BookOpen size={19} /></span><div><h2>Your knowledge library</h2><p>Private documents. Useful answers.</p></div><span className="ai-count">{documents.length}</span></div>
        <div className={`ai-dropzone ${dragging ? 'dragging' : ''} ${uploading ? 'uploading' : ''}`} onDragOver={event => { event.preventDefault(); if (!uploading) setDragging(true) }} onDragLeave={event => { if (!event.currentTarget.contains(event.relatedTarget as Node)) setDragging(false) }} onDrop={event => { event.preventDefault(); setDragging(false); if (event.dataTransfer.files.length > 1) { setUploadError('Please upload one document at a time.'); return } const file = event.dataTransfer.files[0]; if (file) void upload(file) }}>
          <input type="file" className="ai-sr-only" accept=".pdf,.docx,.txt" ref={fileInput} aria-label="Upload document" disabled={uploading} onChange={event => { const file = event.target.files?.[0]; if (file) void upload(file) }} />
          {uploading ? <><Loader2 size={27} className="ai-spin" /><strong>{uploadProgress < 100 ? `Uploading ${uploadProgress}%` : 'Preparing your document…'}</strong><span className="ai-file-name">{uploadName}</span><div className="ai-progress" role="progressbar" aria-label="Document upload" aria-valuenow={uploadProgress} aria-valuemin={0} aria-valuemax={100}><span style={{ width: `${uploadProgress}%` }} /></div><small>{uploadProgress === 100 ? 'Reading the text so you can ask questions.' : 'Your document is on its way.'}</small></> : <><span className="ai-upload-icon"><UploadCloud size={25} strokeWidth={1.5} /></span><strong>Bring your documents to life</strong><p>Drop a file here, or browse to upload.</p><button type="button" className="ai-button secondary" onClick={() => fileInput.current?.click()}><Plus size={15} /> Choose file</button><span className="ai-file-types">PDF <i /> DOCX <i /> TXT <span>· Up to 25 MB</span></span></>}
        </div>
        {uploadError && <Notice>{uploadError}</Notice>}
        {uploadSuccess && <p className="ai-upload-success" role="status"><CheckCircle2 size={15} />{uploadSuccess}</p>}
        <div className="ai-library-list-heading"><h3>Uploaded documents</h3>{documents.length > 0 && <button type="button" className="ai-text-button" onClick={() => setSelectedId('')}>Use all</button>}</div>
        {documents.length > 3 && <label className="ai-document-search"><Search size={15} /><input value={documentSearch} onChange={event => setDocumentSearch(event.target.value)} placeholder="Find a document…" aria-label="Search documents" /></label>}
        {documentsError ? <Notice onRetry={() => void loadDocuments()}>{documentsError}</Notice> : documentsLoading ? <div className="ai-library-loading" role="status"><Loader2 className="ai-spin" size={16} />Loading your library…</div> : !documents.length ? <div className="ai-library-empty"><FileText size={23} strokeWidth={1.4} /><p>A home for your knowledge.</p><span>Your uploaded documents will appear here.</span></div> : <div className="ai-document-list">{visibleDocuments.length ? visibleDocuments.map(document => <div className={`ai-document ${selectedId === document.id ? 'selected' : ''}`} key={document.id} draggable onDragStart={event => event.dataTransfer.setData('application/x-document-id', document.id)}>
          <button type="button" className="ai-document-select" aria-label={`Select ${document.original_filename}`} aria-pressed={selectedId === document.id} onClick={() => setSelectedId(selectedId === document.id ? '' : document.id)}><span className={`ai-file-icon ${document.file_type}`}><FileText size={19} /><small>{document.file_type}</small></span><span className="ai-document-info"><strong title={document.original_filename}>{document.original_filename}</strong><small>{sizeLabel(document.file_size_bytes)} <span>·</span> {document.status === 'READY' ? 'Ready to explore' : document.status.toLowerCase()}</small></span>{selectedId === document.id && <Check size={15} />}</button>
          <div className="ai-document-actions"><button type="button" onClick={() => void inspectDocument(document)}><BookOpen size={12} /> View text</button><button type="button" disabled={ragLoading} onClick={() => void askDocument(DOCUMENT_PROMPTS[0].prompt, document.id)}><Sparkles size={12} /> Summarize</button><button type="button" aria-label={`Delete ${document.original_filename}`} onClick={() => { setDeleting(document); setDeleteError('') }}><Trash2 size={13} /></button></div>
        </div>) : <p className="ai-no-matches">No matching documents.</p>}</div>}
        <div className="ai-library-footer"><ShieldCheck size={15} /><span>Only your account can access these documents.</span></div>
      </aside>

      <div className="ai-rag-main" onDragOver={event => { if (event.dataTransfer.types.includes('application/x-document-id')) event.preventDefault() }} onDrop={event => { const id = event.dataTransfer.getData('application/x-document-id'); if (documents.some(document => document.id === id)) { event.preventDefault(); setSelectedId(id) } }}>
        <div className="ai-rag-intro"><span className="ai-eyebrow">LET YOUR KNOWLEDGE DO THE TALKING</span><h2>Answers with a paper trail.</h2><p>Ask a question. Get an answer grounded in your documents, with sources you can check.</p></div>
        <div className="ai-rag-question ai-panel"><div className="ai-rag-question-heading"><span><FileText size={15} />{selectedDocument ? <strong title={selectedDocument.original_filename}>{selectedDocument.original_filename}</strong> : 'All your documents'}{selectedDocument && <button type="button" className="ai-icon-button" aria-label="Clear document selection" onClick={() => setSelectedId('')}><X size={13} /></button>}</span><select aria-label="Document answer model" value={ragProvider} disabled={ragLoading} onChange={event => setRagProvider(event.target.value as Provider)}>{PROVIDER_IDS.map(id => <option value={id} key={id}>{PROVIDERS[id].name}</option>)}</select></div>
          <textarea value={question} maxLength={2000} rows={3} onChange={event => setQuestion(event.target.value)} onKeyDown={event => submitShortcut(event, () => void askDocument())} aria-label="Document question" placeholder={selectedDocument ? `Ask a question about "${selectedDocument.original_filename}"…` : 'Ask a question across all uploaded documents…'} />
          <div className="ai-rag-question-footer"><span><ShieldCheck size={13} /> Answers from your sources</span><button type="button" className="ai-button primary" aria-label="Query" disabled={ragLoading || !question.trim()} onClick={() => void askDocument()}>{ragLoading ? <Loader2 size={16} className="ai-spin" /> : <Sparkles size={15} />}{ragLoading ? 'Finding an answer…' : 'Ask documents'}{!ragLoading && <ArrowRight size={15} />}</button></div>
        </div>
        <div className="ai-suggestions"><span>Start with</span>{DOCUMENT_PROMPTS.map(item => <button type="button" key={item.label} disabled={ragLoading} onClick={() => documents.length ? void askDocument(item.prompt) : setQuestion(item.prompt)}>{item.label}<ArrowUp size={12} /></button>)}</div>
        {ragError && <Notice onRetry={() => void askDocument()}>{ragError}</Notice>}
        {ragLoading ? <div className="ai-panel ai-answer-panel"><LoadingAnswer label="Reading your sources and connecting the details…" /></div> : ragResult ? <div className="ai-panel ai-answer-panel"><div className="ai-answer-heading"><span className="ai-soft-icon"><Sparkles size={18} /></span><div><h3>{ragResult.status === 'INSUFFICIENT_INFO' ? 'More context is needed' : 'Here’s what your documents say'}</h3><span>{ragResult.model_used} · {(ragResult.latency_ms / 1000).toFixed(1)}s</span></div><CopyButton text={ragResult.answer} /></div><p className="ai-answered-question">{ragResult.query}</p><Answer text={ragResult.answer} sources={ragResult.sources} onCitation={setCitation} />
          {ragResult.sources.length > 0 && <div className="ai-sources"><div className="ai-sources-heading"><h4>Sources</h4><span>{ragResult.sources.length} references · click to verify</span></div><div className="ai-source-grid">{ragResult.sources.map(source => <button type="button" key={source.chunk_id} className="ai-source-card" onClick={() => setCitation(source)}><span className="ai-source-number">{source.index}</span><span><strong>{source.filename}</strong><small>{source.page_number ? `Page ${source.page_number}` : 'Document excerpt'}</small><p>{source.snippet}</p></span><ArrowRight size={14} /></button>)}</div></div>}
        </div> : <div className="ai-rag-empty"><EmptyState title="Your documents have the answers." icon="file">Upload a document, ask a question, and follow the sources.<br />Every answer starts with your knowledge.</EmptyState><div className="ai-how-it-works"><span><b>01</b> Add a document</span><ChevronRight size={14} /><span><b>02</b> Ask a question</span><ChevronRight size={14} /><span><b>03</b> Explore the sources</span></div></div>}
      </div>
    </section>}

    <footer className="ai-workspace-footer"><span><ShieldCheck size={13} /> Private workspace</span><span>Built for a little more clarity.</span></footer>

    {citation && <Dialog title={`Source ${citation.index}`} onClose={() => setCitation(null)} wide><div className="ai-citation-detail"><div className="ai-source-file"><FileText size={22} /><div><h3>{citation.filename}</h3><span>{citation.page_number ? `Page ${citation.page_number}` : 'Document excerpt'} · Original source text</span></div><CopyButton text={citation.snippet} label="Copy source text" /></div><blockquote>{citation.snippet}</blockquote><p>Compare this excerpt with the answer to verify the details.</p></div></Dialog>}
    {inspecting && <Dialog title="Document text" onClose={() => { inspectRequest.current++; setInspecting(null) }} wide><div className="ai-inspect"><div className="ai-source-file"><FileText size={22} /><div><h3>{inspecting.original_filename}</h3><span>{sizeLabel(inspecting.file_size_bytes)} · {inspecting.chunk_count} passages</span></div></div>{inspectError ? <Notice>{inspectError}</Notice> : inspectLoading ? <LoadingAnswer label="Opening document text…" /> : inspecting.chunks.length ? inspecting.chunks.map(chunk => <article className="ai-passage" key={chunk.chunk_id}><span>PASSAGE {chunk.chunk_index + 1}{chunk.page_number ? ` · PAGE ${chunk.page_number}` : ''}</span><p>{chunk.content}</p></article>) : <p className="ai-no-matches">No readable passages are available for this document.</p>}</div></Dialog>}
    {deleting && <Dialog title="Delete this document?" onClose={() => setDeleting(null)} busy={deleteLoading}><div className="ai-delete-content"><span className="ai-delete-icon"><Trash2 size={23} /></span><p><strong>{deleting.original_filename}</strong> will be removed from your library and future document searches.</p><p>You can upload it again later.</p>{deleteError && <Notice>{deleteError}</Notice>}<div className="ai-dialog-actions"><button type="button" className="ai-button secondary" disabled={deleteLoading} onClick={() => setDeleting(null)}>Keep document</button><button type="button" className="ai-button danger" disabled={deleteLoading} onClick={() => void deleteDocument()}>{deleteLoading ? <Loader2 size={15} className="ai-spin" /> : <Trash2 size={15} />}{deleteLoading ? 'Deleting…' : 'Delete document'}</button></div></div></Dialog>}
  </div>
}
