import React, { useEffect, useId, useRef, useState } from 'react'
import { AlertCircle, Check, Copy, FileText, Loader2, Sparkles, X } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { CitationSource } from '../../api/aiAssistantApi'

export const PROVIDERS = {
  openai: { name: 'OpenAI', letter: 'O', color: 'green', description: 'A different perspective, side by side.' },
  claude: { name: 'Claude', letter: 'C', color: 'terra', description: 'Another approach to the same question.' },
  gemini: { name: 'Gemini', letter: 'G', color: 'blue', description: 'One more perspective to explore.' },
} as const
export type Provider = keyof typeof PROVIDERS
export const PROVIDER_IDS = Object.keys(PROVIDERS) as Provider[]

export function ProviderMark({ provider, small = false }: { provider: Provider; small?: boolean }) {
  const meta = PROVIDERS[provider]
  return <span aria-hidden="true" className={`ai-provider-mark ${meta.color} ${small ? 'small' : ''}`}>{provider === 'gemini' ? <Sparkles size={small ? 15 : 21} /> : meta.letter}</span>
}

export function Notice({ children, onRetry }: { children: React.ReactNode; onRetry?: () => void }) {
  return <div className="ai-notice" role="alert"><AlertCircle size={17} /><span>{children}</span>{onRetry && <button type="button" onClick={onRetry}>Try again</button>}</div>
}

export function CopyButton({ text, label = 'Copy answer' }: { text: string; label?: string }) {
  const [state, setState] = useState<'idle' | 'copied' | 'error'>('idle')
  useEffect(() => {
    if (state === 'idle') return
    const timer = window.setTimeout(() => setState('idle'), 2200)
    return () => window.clearTimeout(timer)
  }, [state])
  return <button type="button" className="ai-icon-button" aria-label={state === 'copied' ? 'Copied' : label} title={state === 'error' ? 'Could not copy. Select the text to copy it.' : state === 'copied' ? 'Copied' : label} onClick={async () => {
    try { await navigator.clipboard.writeText(text); setState('copied') } catch { setState('error') }
  }}>{state === 'copied' ? <Check size={15} /> : state === 'error' ? <AlertCircle size={15} /> : <Copy size={15} />}</button>
}

export function Answer({ text, sources = [], onCitation }: { text: string; sources?: CitationSource[]; onCitation?: (source: CitationSource) => void }) {
  function linkCitations(children: React.ReactNode): React.ReactNode {
    return React.Children.map(children, child => {
      if (typeof child !== 'string' || !onCitation) return child
      return child.split(/(\[\d+\])/).map((part, index) => {
        const source = /^\[(\d+)\]$/.test(part) ? sources.find(item => item.index === Number(part.slice(1, -1))) : undefined
        return source ? <button type="button" key={index} className="ai-inline-citation" onClick={() => onCitation(source)} aria-label={`View source ${source.index}: ${source.filename}`}>{part}</button> : part
      })
    })
  }
  return <div className="ai-answer"><ReactMarkdown remarkPlugins={[remarkGfm]} components={{
    p: ({ children }) => <p>{linkCitations(children)}</p>,
    li: ({ children }) => <li>{linkCitations(children)}</li>,
    a: ({ href, children }) => <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>,
    table: ({ children }) => <div className="ai-table-scroll"><table>{children}</table></div>,
  }}>{text}</ReactMarkdown></div>
}

export function LoadingAnswer({ label = 'Thinking through your question…' }: { label?: string }) {
  return <div className="ai-loading" role="status"><div className="ai-loading-label"><Loader2 size={16} className="ai-spin" />{label}</div><div className="ai-skeleton" /><div className="ai-skeleton" /><div className="ai-skeleton short" /></div>
}

export function EmptyState({ title, children, icon = 'sparkles' }: { title: string; children: React.ReactNode; icon?: 'sparkles' | 'file' }) {
  return <div className="ai-empty"><span className="ai-empty-icon">{icon === 'file' ? <FileText size={26} strokeWidth={1.4} /> : <Sparkles size={27} strokeWidth={1.4} />}</span><h3>{title}</h3><p>{children}</p></div>
}

export function Dialog({ title, onClose, busy = false, children, wide = false }: { title: string; onClose: () => void; busy?: boolean; children: React.ReactNode; wide?: boolean }) {
  const titleId = useId()
  const ref = useRef<HTMLDivElement>(null)
  const closeRef = useRef(onClose)
  closeRef.current = onClose
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null
    const overflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    ref.current?.focus()
    return () => { document.body.style.overflow = overflow; previous?.focus() }
  }, [])
  return <div className="ai-modal-backdrop" onMouseDown={event => { if (event.target === event.currentTarget && !busy) onClose() }}>
    <div className={`ai-dialog ${wide ? 'wide' : ''}`} role="dialog" aria-modal="true" aria-labelledby={titleId} ref={ref} tabIndex={-1} onKeyDown={event => {
      if (event.key === 'Escape' && !busy) { event.stopPropagation(); closeRef.current() }
      if (event.key === 'Tab') {
        const focusable = Array.from(ref.current?.querySelectorAll<HTMLElement>('button:not([disabled]), a[href], input, select, textarea, [tabindex="0"]') || [])
        const first = focusable[0], last = focusable[focusable.length - 1]
        if (!first) { event.preventDefault(); return }
        if (event.shiftKey && (document.activeElement === first || document.activeElement === ref.current)) { event.preventDefault(); last.focus() }
        else if (!event.shiftKey && (document.activeElement === last || document.activeElement === ref.current)) { event.preventDefault(); first.focus() }
      }
    }}><div className="ai-dialog-heading"><h2 id={titleId}>{title}</h2><button type="button" className="ai-icon-button" aria-label="Close dialog" disabled={busy} onClick={onClose}><X size={19} /></button></div>{children}</div>
  </div>
}
