import React, { useCallback, useEffect, useRef, useState } from 'react'
import { ArrowUp, BookOpen, BriefcaseBusiness, Check, CheckCircle2, ExternalLink, FileText, Loader2, Pencil, Plus, RefreshCw, Sparkles, Trash2, UploadCloud, UserRound } from 'lucide-react'
import { getAssistantError, type CitationSource, type ModelStatus } from '../../api/aiAssistantApi'
import { profileIntelligenceApi as api, type ProfileSnapshot, type ProfileScope, type ProfileAnswer, type JobMatch, type JobTarget, type TargetJob } from '../../api/profileIntelligenceApi'
import { Answer, CopyButton, Dialog, EmptyState, LoadingAnswer, Notice, PROVIDER_IDS, PROVIDERS, type Provider } from './AssistantUI'
import './profile-ai.css'

type ChatEntry = { question: string; answers: ProfileAnswer[] }
const profileFields = [
  ['first_name', 'First name'], ['last_name', 'Last name'], ['degree', 'Degree'],
  ['department', 'Department'], ['institution_name', 'Institution'],
  ['github_url', 'GitHub URL'], ['linkedin_url', 'LinkedIn URL'], ['portfolio_url', 'Portfolio URL'],
] as const
const safeLink = (url?: string | null) => url && /^https?:\/\//i.test(url) ? url : undefined

export default function ProfileAI({ models, onOpenDocuments }: { models: ModelStatus[]; onOpenDocuments: () => void }) {
  const [data, setData] = useState<ProfileSnapshot | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busy, setBusy] = useState(false)
  const [progress, setProgress] = useState(0)
  const [view, setView] = useState<'overview' | 'resume' | 'job'>('overview')
  const [dialog, setDialog] = useState<'profile' | 'project' | 'skill' | 'delete' | null>(null)
  const [form, setForm] = useState<Record<string, string>>({})
  const [formError, setFormError] = useState('')
  const [citation, setCitation] = useState<CitationSource | null>(null)
  const [jobs, setJobs] = useState<TargetJob[]>([])
  const [jobsError, setJobsError] = useState('')
  const [jobId, setJobId] = useState('')
  const [jd, setJd] = useState('')
  const [requiredSkills, setRequiredSkills] = useState('')
  const [match, setMatch] = useState<JobMatch | null>(null)
  const [matchBusy, setMatchBusy] = useState(false)
  const [matchError, setMatchError] = useState('')
  const [provider, setProvider] = useState<Provider>('gemini')
  const [compare, setCompare] = useState(false)
  const [scope, setScope] = useState<ProfileScope>('profile')
  const [projectId, setProjectId] = useState('')
  const [documentId, setDocumentId] = useState('')
  const [question, setQuestion] = useState('')
  const [entries, setEntries] = useState<ChatEntry[]>([])
  const [chatBusy, setChatBusy] = useState(false)
  const [chatError, setChatError] = useState('')
  const fileInput = useRef<HTMLInputElement>(null)
  const snapshot = useRef<ProfileSnapshot | null>(null)
  const loadSequence = useRef(0)
  const chatSequence = useRef(0)
  const matchSequence = useRef(0)
  const mutationLock = useRef(false)
  const chatLock = useRef(false)
  const matchLock = useRef(false)
  const mounted = useRef(true)
  const providerInitialized = useRef(false)
  const chatEnd = useRef<HTMLDivElement>(null)

  function adopt(next: ProfileSnapshot) {
    if (snapshot.current && snapshot.current.version !== next.version) {
      setEntries([]); setMatch(null); setCitation(null)
      chatSequence.current++; matchSequence.current++
      setChatBusy(false); setMatchBusy(false); chatLock.current = false; matchLock.current = false
    }
    snapshot.current = next
    setData(next)
  }
  const load = useCallback(async () => {
    const sequence = ++loadSequence.current
    try {
      const response = await api.overview()
      if (!mounted.current || sequence !== loadSequence.current) return
      adopt(response.data.data); setError('')
    } catch (err) {
      if (mounted.current && sequence === loadSequence.current) setError(getAssistantError(err, 'Could not load your profile.'))
    } finally { if (mounted.current && sequence === loadSequence.current) setLoading(false) }
  }, [])

  useEffect(() => {
    mounted.current = true
    void load()
    void api.jobs().then(response => { if (mounted.current) setJobs(response.data.data) })
      .catch(err => { if (mounted.current) setJobsError(getAssistantError(err, 'Could not load jobs. You can still paste a description.')) })
    const onFocus = () => { void load() }
    window.addEventListener('focus', onFocus)
    return () => { mounted.current = false; loadSequence.current++; chatSequence.current++; matchSequence.current++; window.removeEventListener('focus', onFocus) }
  }, [load])
  const processing = data?.resume?.status === 'PENDING' || data?.resume?.status === 'PROCESSING'
  useEffect(() => {
    if (!processing) return
    const timer = window.setInterval(() => void load(), 2500)
    return () => window.clearInterval(timer)
  }, [processing, load])
  useEffect(() => {
    if (!providerInitialized.current && models.some(model => model.is_configured)) {
      const available = models.find(model => model.provider === 'gemini' && model.is_configured) || models.find(model => model.is_configured)
      if (available && PROVIDER_IDS.includes(available.provider as Provider)) setProvider(available.provider as Provider)
      providerInitialized.current = true
    }
  }, [models])
  useEffect(() => { chatEnd.current?.scrollIntoView({ block: 'nearest', behavior: 'smooth' }) }, [entries, chatBusy])

  function clearConversation() { chatSequence.current++; chatLock.current = false; setChatBusy(false); setEntries([]); setChatError(''); setCitation(null) }
  function changeTarget() { matchSequence.current++; matchLock.current = false; setMatchBusy(false); setMatch(null); setMatchError(''); if (scope === 'job') clearConversation() }
  function target(): JobTarget {
    return jobId ? { job_id: jobId } : { job_description: jd.trim(), required_skills: requiredSkills.split(',').map(value => value.trim()).filter(Boolean) }
  }
  async function mutate(action: () => Promise<unknown>, success: string) {
    if (mutationLock.current) return
    mutationLock.current = true; setBusy(true); setError(''); setFormError(''); setNotice('')
    // Discard older reads and generations before changing source data.
    loadSequence.current++; clearConversation(); changeTarget()
    try {
      await action()
      if (!mounted.current) return
      setDialog(null); setNotice(success)
      await load()
    } catch (err) {
      if (mounted.current) { const message = getAssistantError(err, 'Could not save the change.'); setFormError(message); setError(message) }
    } finally { if (mounted.current) setBusy(false); mutationLock.current = false }
  }
  async function upload(file?: File) {
    if (!file) return
    if (!/\.(pdf|docx|doc)$/i.test(file.name)) { setError('Choose a PDF or Word resume.'); return }
    const limit = data?.limits?.resume_max_size_mb ?? 5
    if (file.size > limit * 1024 * 1024) { setError('Your resume must be ' + limit + ' MB or smaller.'); return }
    setProgress(0)
    await mutate(() => api.uploadResume(file, setProgress), 'Resume saved. Analysis will update automatically.')
    if (fileInput.current) fileInput.current.value = ''
  }
  function editProfile() {
    setForm(Object.fromEntries([...profileFields.map(([key]) => [key, String(data?.profile[key] || '')]), ['summary', String(data?.profile.summary || '')]]))
    setFormError(''); setDialog('profile')
  }
  function addSkill(name = '') { setForm({ name, proficiency_level: 'BEGINNER' }); setFormError(''); setDialog('skill') }
  function saveForm(event: React.FormEvent) {
    event.preventDefault()
    if (dialog === 'profile') void mutate(() => api.saveProfile(Object.fromEntries(Object.entries(form).map(([key, value]) => [key, value.trim() || null]))), 'Profile updated.')
    if (dialog === 'skill') void mutate(() => api.addSkill(form.name.trim(), form.proficiency_level), 'Skill added as self-reported.')
    if (dialog === 'project') void mutate(() => api.addProject({ title: form.title.trim(), description: form.description.trim(), technologies: form.technologies.split(',').map(value => value.trim()).filter(Boolean), project_url: form.project_url.trim() || null }), 'Project saved.')
  }
  async function analyzeJob() {
    if (matchLock.current || !data) return
    if (!jobId && jd.trim().length < 20) { setMatchError('Paste a job description of at least 20 characters, or choose a saved job.'); return }
    matchLock.current = true; setMatchBusy(true); setMatchError('')
    const sequence = ++matchSequence.current
    try {
      const response = await api.match(target())
      if (!mounted.current || sequence !== matchSequence.current) return
      if (response.data.data.version !== snapshot.current?.version) { await load(); setMatchError('Your profile changed. Run the comparison again.'); return }
      setMatch(response.data.data)
    } catch (err) { if (mounted.current && sequence === matchSequence.current) setMatchError(getAssistantError(err, 'Could not compare this job.')) }
    finally { if (sequence === matchSequence.current) { setMatchBusy(false); matchLock.current = false } }
  }
  async function ask(override?: string) {
    const text = (override || question).trim()
    if (!text || !data || chatLock.current || busy) return
    const activeScope = override ? 'profile' : scope
    if (activeScope === 'project' && !projectId) { setChatError('Choose a project first.'); return }
    if (activeScope === 'job' && !jobId && jd.trim().length < 20) { setView('job'); setChatError('Choose a job or paste its description first.'); return }
    if (override && scope !== 'profile') { clearConversation(); setScope('profile') }
    chatLock.current = true; setChatBusy(true); setChatError('')
    const sequence = ++chatSequence.current
    const history = override && scope !== 'profile' ? [] : entries.flatMap(entry => [
      { role: 'user' as const, content: entry.question.slice(0, 4000) },
      ...entry.answers.filter(answer => answer.status === 'SUCCESS').slice(0, 1).map(answer => ({ role: 'assistant' as const, content: answer.answer.slice(0, 4000) })),
    ]).slice(-10)
    try {
      const response = await api.chat({
        question: text, provider, compare, scope: activeScope, version: data.version, conversation_history: history,
        project_id: activeScope === 'project' ? projectId : undefined,
        document_id: (activeScope === 'documents' || activeScope === 'project') && documentId ? documentId : undefined,
        target: activeScope === 'job' ? target() : undefined,
      })
      if (!mounted.current || sequence !== chatSequence.current) return
      setEntries(previous => [...previous, { question: text, answers: response.data.data.answers }]); setQuestion('')
    } catch (err) {
      if (mounted.current && sequence === chatSequence.current) { setChatError(getAssistantError(err, 'Could not answer your question.')); void load() }
    } finally { if (sequence === chatSequence.current) { setChatBusy(false); chatLock.current = false } }
  }

  if (loading) return <LoadingAnswer label="Connecting your profile and saved resume…" />
  if (!data) return <Notice onRetry={() => void load()}>{error || 'Your profile could not be loaded.'}</Notice>
  const analysis = data.resume?.analysis
  const name = [data.profile.first_name, data.profile.last_name].filter(Boolean).join(' ') || 'Your profile'
  const status = !data.resume ? 'No resume saved' : processing ? 'Analyzing resume' : data.resume.status === 'READY' ? 'Analysis ready' : 'Needs attention'

  return <section className="profile-ai ai-enter" aria-label="My Profile AI">
    {error && <Notice onRetry={() => void load()}>{error}</Notice>}
    {notice && <p className="pa-success" role="status"><CheckCircle2 size={16} />{notice}</p>}
    <div className="pa-hero">
      <div className="pa-identity"><span className="pa-avatar"><UserRound size={28} /></span><div><span className="ai-eyebrow">YOUR EXPERIENCE, CONNECTED</span><h2>{name}</h2><p>Know your strengths. Show your evidence. Plan your next step.</p></div></div>
      <div className="pa-hero-actions"><span className={'pa-state ' + (processing ? 'processing' : data.resume?.status === 'READY' ? 'ready' : '')}>{processing ? <Loader2 size={13} className="ai-spin" /> : <FileText size={13} />}{status}</span><button className="ai-button secondary" onClick={editProfile} disabled={busy}><Pencil size={14} />Edit profile</button></div>
    </div>
    <div className="pa-summary">
      <div><div className="pa-card-title"><Sparkles size={17} /><h3>Your profile in three lines</h3><CopyButton text={data.summary.join('\n')} label="Copy profile summary" /></div><ol>{data.summary.map((line, index) => <li key={index}>{line}</li>)}</ol><span className="pa-caption">Based on saved profile facts and recognized resume mentions.</span></div>
      <div className="pa-stats"><div><strong>{data.skills.length}</strong><span>Profile skills</span></div><div><strong>{data.projects.length}</strong><span>Saved projects</span></div><div><strong>{analysis?.skills.length ?? '—'}</strong><span>Resume mentions</span></div></div>
    </div>
    <div className="pa-layout">
      <div className="pa-main">
        <div className="pa-views" aria-label="Profile sections">{(['overview', 'resume', 'job'] as const).map(item => <button key={item} aria-pressed={view === item} onClick={() => setView(item)}>{item === 'overview' ? 'Skills & projects' : item === 'resume' ? 'Resume review' : 'Job match'}</button>)}</div>
        <article className="pa-card pa-resume-file">
          <FileText size={23} /><div><strong>{data.resume?.filename || 'Connect your resume'}</strong><p>{processing ? 'Extraction runs in the background. This page updates automatically.' : data.resume?.updated_at ? 'Last processed ' + new Date(data.resume.updated_at).toLocaleString() : 'Use the resume saved in your profile, or upload one here.'}</p><small>PDF or Word · up to {data.limits?.resume_max_size_mb ?? 5} MB. Older DOC files need conversion for analysis.</small></div>
          <div className="pa-file-actions"><input ref={fileInput} type="file" accept=".pdf,.docx,.doc" aria-label="Upload profile resume" className="ai-sr-only" onChange={event => void upload(event.target.files?.[0])} disabled={busy} /><button className="ai-button secondary" onClick={() => fileInput.current?.click()} disabled={busy}><UploadCloud size={14} />{busy ? 'Saving ' + progress + '%' : data.resume ? 'Replace' : 'Upload resume'}</button>{data.resume && <><button className="ai-icon-button" aria-label="Retry resume analysis" disabled={busy || processing} onClick={() => void mutate(() => api.refresh(), 'Analysis queued.')}><RefreshCw size={16} /></button><button className="ai-icon-button" aria-label="Delete saved resume" disabled={busy} onClick={() => { setFormError(''); setDialog('delete') }}><Trash2 size={16} /></button></>}</div>
        </article>
        {data.resume?.error && <Notice>{data.resume.error}</Notice>}
        {analysis?.warnings?.map(warning => <Notice key={warning}>{warning}</Notice>)}
        {view === 'overview' && <>
          <article className="pa-card"><div className="pa-card-title"><CheckCircle2 size={18} /><h3>Skills in your profile</h3><button className="pa-text-button" onClick={() => addSkill()}><Plus size={14} />Add skill</button></div><p className="pa-caption">Source labels describe how a skill was recorded. They do not independently verify proficiency.</p><div className="pa-skills">{data.skills.map(skill => <div className="pa-skill" key={skill.id}><strong>{skill.name}</strong><small>{skill.proficiency_level.toLowerCase()} · {skill.source.toLowerCase()}</small></div>)}</div>{!data.skills.length && <p className="pa-muted">Add your skills, or review suggestions from your resume below.</p>}
          {data.suggested_skills.length > 0 && <div className="pa-suggestions-block"><h4>Found in your resume</h4><p className="pa-caption">Review each skill before adding it to your profile.</p><div className="pa-suggestion-chips">{data.suggested_skills.map(skill => <button key={skill.name} title={skill.evidence.quote} onClick={() => addSkill(skill.name)} disabled={busy}><Plus size={13} />{skill.name}</button>)}</div></div>}</article>
          <article className="pa-card"><div className="pa-card-title"><BriefcaseBusiness size={18} /><h3>Projects & links</h3><button className="pa-text-button" onClick={() => { setForm({ title: '', description: '', technologies: '', project_url: '' }); setFormError(''); setDialog('project') }}><Plus size={14} />Add project</button></div>{data.projects.length ? data.projects.map(project => <div className="pa-project" key={project.id}><div><h4>{project.title}</h4>{safeLink(project.project_url) && <a href={safeLink(project.project_url)} target="_blank" rel="noopener noreferrer" aria-label={'Open ' + project.title + ' link'}><ExternalLink size={14} /></a>}</div><p>{project.description || 'No description saved yet.'}</p><div className="pa-tech">{project.technologies.map(tech => <span key={tech}>{tech}</span>)}</div><button className="pa-text-button" onClick={() => { clearConversation(); setProjectId(project.id); setScope('project') }}>Discuss this project <ArrowUp size={13} /></button></div>) : <p className="pa-muted">Add a project, your contribution and a repository or demo link.</p>}<p className="pa-caption">Links are saved references. Repository contents have not been fetched. Select a supporting document in chat to discuss its contents.</p></article>
          <article className="pa-card" aria-label="Subject and learning links">
            <div className="pa-card-title"><BookOpen size={18} /><h3>Subject & learning links</h3></div>
            <p className="pa-caption">Learning catalogue links matched to your recorded skills, project technologies and field of study. Website contents have not been fetched.</p>
            {data.learning_resources?.length ? data.learning_resources.map(resource => <a className="pa-resource" key={resource.id} href={safeLink(resource.url)} target="_blank" rel="noopener noreferrer"><span><strong>{resource.title}</strong><small>{resource.skills.join(', ')} · {resource.provider || 'Learning catalogue'}{resource.is_free ? ' · Free' : ''}</small></span><ExternalLink size={15} /></a>) : <p className="pa-muted">No matching links are available in your learning catalogue yet.</p>}
            <h4 className="pa-mini-heading">Discuss your study notes</h4>
            <p className="pa-caption">Choose a ready document to ask questions with citations, or upload PDF, DOCX or TXT notes.</p>
            {data.documents.filter(doc => doc.status === 'READY').map(doc => <button className="pa-document-link" key={doc.id} onClick={() => { clearConversation(); setDocumentId(doc.id); setScope('documents') }}><FileText size={14} /><span>{doc.filename}</span><ArrowUp size={13} /></button>)}
            <button className="pa-text-button" onClick={onOpenDocuments}>Upload or manage study documents <ExternalLink size={13} /></button>
          </article>
          {(data.certifications.length > 0 || data.internships.length > 0) && <article className="pa-card"><div className="pa-card-title"><BookOpen size={18} /><h3>Experience & credentials</h3></div>{data.internships.map(item => <p className="pa-record" key={item.id}>{item.role} · {item.company_name}</p>)}{data.certifications.map(item => <p className="pa-record" key={item.id}>{item.name}{item.issuer && ' · ' + item.issuer}</p>)}</article>}
        </>}
        {view === 'resume' && (analysis ? <>
          <article className="pa-card"><div className="pa-card-title"><CheckCircle2 size={18} /><h3>Resume quality checklist</h3><span className="pa-count">{analysis.quality.passed}/{analysis.quality.total}</span></div><p className="pa-caption">{analysis.quality.note}</p><div className="pa-checks">{analysis.quality.checks.map(check => <div key={check.id}><span className={'pa-check-icon ' + (check.passed ? 'pass' : '')}>{check.passed ? <Check size={14} /> : '·'}</span><div><strong>{check.label}</strong><p>{check.detail}</p></div></div>)}</div></article>
          <article className="pa-card"><div className="pa-card-title"><Sparkles size={18} /><h3>Your next improvements</h3><CopyButton text={data.improvement_summary.join('\n')} label="Copy improvement summary" /></div><ol className="pa-improvements">{data.improvement_summary.map((line, i) => <li key={i}>{line}</li>)}</ol>{data.profile_only_skills.length > 0 && <p className="pa-callout">Present in profile, not found in resume: <strong>{data.profile_only_skills.join(', ')}</strong>. Add relevant evidence only where accurate.</p>}</article>
          <article className="pa-card"><div className="pa-card-title"><FileText size={18} /><h3>What we could read</h3><span className="pa-count">{analysis.word_count} words</span></div>{Object.entries(analysis.sections).map(([key, lines]) => <details className="pa-extracted" key={key}><summary>{key}</summary>{lines.map((line, i) => <p key={i}>{line.text}{line.page_number != null && <small> · p. {line.page_number}</small>}</p>)}</details>)}{analysis.links.map(link => <a className="pa-saved-link" key={link.url} href={safeLink(link.url)} target="_blank" rel="noopener noreferrer">{link.url}<ExternalLink size={13} /></a>)}</article>
        </> : <article className="pa-card"><EmptyState title={processing ? 'Your resume is being analyzed' : 'Resume feedback starts here'} icon="file">{processing ? 'Text extraction and source indexing are in progress.' : 'Upload a readable PDF or DOCX to see skills, sections and quality feedback.'}</EmptyState></article>)}
        {view === 'job' && <article className="pa-card"><div className="pa-card-title"><BriefcaseBusiness size={18} /><h3>Compare with a target job</h3></div><p className="pa-caption">See what your submitted resume actually mentions, separately from your profile.</p>{jobsError && <Notice>{jobsError}</Notice>}
          <label className="pa-field">Target job<select value={jobId} onChange={event => { changeTarget(); setJobId(event.target.value) }}><option value="">Paste a job description</option>{jobs.map(job => <option key={job.id} value={job.id}>{job.title} · {job.company_name}</option>)}</select></label>
          {!jobId && <><label className="pa-field">Job description<textarea value={jd} rows={5} maxLength={20000} placeholder="Paste the responsibilities and requirements…" onChange={event => { changeTarget(); setJd(event.target.value) }} /></label><label className="pa-field">Required skills (optional, comma separated)<input value={requiredSkills} maxLength={3000} placeholder="Python, SQL, Docker" onChange={event => { changeTarget(); setRequiredSkills(event.target.value) }} /></label><p className="pa-caption">Without a confirmed list, we detect skill mentions. Review them because optional requirements may also appear.</p></>}
          <button className="ai-button primary pa-wide" disabled={matchBusy || busy} onClick={() => void analyzeJob()}>{matchBusy ? <Loader2 size={16} className="ai-spin" /> : <Sparkles size={16} />}{matchBusy ? 'Comparing evidence…' : 'Compare job requirements'}</button>
          {matchError && <Notice>{matchError}</Notice>}
          {match && <div className="pa-match-result"><div className="pa-coverage"><div><strong>{match.resume_coverage.percent == null ? '—' : match.resume_coverage.percent + '%'}</strong><span>Resume keyword coverage</span><small>{match.resume_coverage.found}/{match.resume_coverage.total} found in resume</small></div><div><strong>{match.profile_coverage.found}/{match.profile_coverage.total}</strong><span>Recorded in profile</span><small>Includes saved project technologies</small></div></div><p className="pa-caption">{match.note}</p><p className="pa-callout">{match.requirements_note}</p>{!jobId && match.target.requirements_origin === 'detected_mentions' && match.target.required_skills.length > 0 && <button className="pa-text-button" onClick={() => { setRequiredSkills(match.target.required_skills.join(', ')); changeTarget() }}>Review detected skills in the required-skills field</button>}
            <div className="pa-match-table"><table><thead><tr><th>Skill</th><th>Resume</th><th>Profile</th></tr></thead><tbody>{match.requirements.map(row => <tr key={row.skill}><td>{row.skill}</td><td><span className={row.resume_status === 'found' ? 'pa-found' : ''}>{row.resume_status.replace('_', ' ')}</span>{row.resume_evidence && <details><summary>Evidence</summary><p>{row.resume_evidence.quote}</p></details>}</td><td>{row.profile_status.replace('_', ' ')}</td></tr>)}</tbody></table></div>{match.requirements.length === 0 && <p className="pa-muted">No recognizable target skills found. Enter an explicit required-skills list.</p>}<ol className="pa-improvements">{match.summary.map((line, i) => <li key={i}>{line}</li>)}</ol>
            {match.resources.length > 0 && <><h4 className="pa-mini-heading">Resources for the gaps</h4>{match.resources.map(resource => <a className="pa-resource" key={resource.id} href={safeLink(resource.url)} target="_blank" rel="noopener noreferrer"><span><strong>{resource.title}</strong><small>{resource.skills.join(', ')} · {resource.provider}{resource.is_free ? ' · Free' : ''}</small></span><ExternalLink size={15} /></a>)}</>}
            {match.project_suggestions.length > 0 && <><h4 className="pa-mini-heading">Suggested practice projects</h4>{match.project_suggestions.map(item => <div className="pa-project" key={item.skill}><h4>{item.title}</h4><p>{item.description}</p></div>)}</>}
          </div>}
        </article>}
      </div>
      <aside className="pa-chat pa-card" aria-label="Profile conversation">
        <div className="pa-card-title"><Sparkles size={18} /><h3>Ask your Profile AI</h3><button className="ai-icon-button" aria-label="Clear profile conversation" onClick={clearConversation}><RefreshCw size={15} /></button></div>
        <p className="pa-caption">{scope === 'profile' || scope === 'project'
          ? 'Explore your saved experience or learn about a recorded skill. Profile answers cite evidence; learning answers are labeled as general knowledge.'
          : 'Answers use only the selected evidence. Click a citation to inspect its source.'}</p>
        <div className="pa-chat-selects"><label className="pa-field">Sources<select value={scope} onChange={event => { clearConversation(); setScope(event.target.value as ProfileScope) }}><option value="profile">Profile, resume & learning</option><option value="resume">Resume only</option><option value="project">Selected project</option><option value="documents">My documents</option><option value="job">Target job & my evidence</option></select></label><label className="pa-field">Model<select value={provider} onChange={event => { clearConversation(); setProvider(event.target.value as Provider) }}>{PROVIDER_IDS.map(id => <option key={id} value={id}>{PROVIDERS[id].name}{models.find(model => model.provider === id)?.is_configured ? '' : ' · unavailable'}</option>)}</select></label></div>
        {scope === 'project' && <label className="pa-field">Project<select value={projectId} onChange={event => { clearConversation(); setProjectId(event.target.value) }}><option value="">Choose a project</option>{data.projects.map(project => <option value={project.id} key={project.id}>{project.title}</option>)}</select></label>}
        {(scope === 'project' || scope === 'documents') && <label className="pa-field">Supporting document<select value={documentId} onChange={event => { clearConversation(); setDocumentId(event.target.value) }}><option value="">{scope === 'project' ? 'Use saved project details' : 'All my ready documents'}</option>{data.documents.filter(doc => doc.status === 'READY').map(doc => <option key={doc.id} value={doc.id}>{doc.filename}</option>)}</select></label>}
        {scope === 'documents' && <button className="pa-text-button" onClick={onOpenDocuments}>Upload or manage documents <ExternalLink size={13} /></button>}
        {scope === 'job' && <button className="pa-text-button" onClick={() => setView('job')}>Edit target job <Pencil size={13} /></button>}
        <label className="pa-checkbox"><input type="checkbox" checked={compare} onChange={event => { clearConversation(); setCompare(event.target.checked) }} />Compare all three models with the same context</label>
        <div className="pa-chat-thread" aria-live="polite">
          {entries.length === 0 && !chatBusy && <div className="pa-chat-welcome"><span><Sparkles size={24} /></span><h4>Your story has useful details.</h4><p>Learn a concept from your skills, discuss your projects, or find evidence for a job requirement.</p><button onClick={() => void ask('List all my skills')}>List all my skills <ArrowUp size={13} /></button><button onClick={() => void ask('Give me a three-line profile summary')}>Write my three-line summary <ArrowUp size={13} /></button><button onClick={() => void ask('List my projects and links')}>Show my projects & links <ArrowUp size={13} /></button><small>These three shortcuts also work without an AI provider.</small></div>}
          {entries.map((entry, index) => <div key={index} className="pa-chat-entry">
            <div className="pa-user-question">{entry.question}</div>
            {entry.answers.map((answer, n) => <div key={n} className="pa-chat-answer">
              <div className="pa-answer-meta"><span>{answer.model}</span>{answer.status === 'SUCCESS' && <CopyButton text={answer.knowledge_note ? 'Skill learning · ' + answer.topic + '\n' + answer.knowledge_note + '\n\n' + answer.answer : answer.answer} />}</div>
              {answer.status === 'SUCCESS' ? <>
                {answer.answer_kind === 'skill_learning'
                  ? <div className="pa-learning-context"><span className="pa-answer-kind"><BookOpen size={13} />Skill learning · {answer.topic}</span><p>{answer.knowledge_note}</p></div>
                  : <span className="pa-answer-kind">{answer.sources.length ? 'Profile evidence' : 'Profile guide'}</span>}
                <Answer text={answer.answer} sources={answer.sources} onCitation={setCitation} />
                {answer.sources.length > 0 && <div className="pa-citations">{answer.sources.map(source => <button key={source.index} onClick={() => setCitation(source)}>[{source.index}] {source.filename}</button>)}</div>}
              </> : <Notice>{answer.error_message || 'This model is unavailable. Choose another model or use a profile shortcut.'}</Notice>}
            </div>)}
          </div>)}
          {chatBusy && <LoadingAnswer label="Checking your question and preparing an answer…" />}<div ref={chatEnd} />
        </div>
        {chatError && <Notice>{chatError}</Notice>}<form className="pa-chat-composer" onSubmit={event => { event.preventDefault(); void ask() }}><label className="ai-sr-only" htmlFor="profile-question">Profile question</label><textarea id="profile-question" value={question} onChange={event => setQuestion(event.target.value)} maxLength={4000} placeholder={scope === 'profile' || scope === 'project' ? 'Ask about your experience or learn a recorded skill…' : 'Ask about the selected evidence…'} rows={3} onKeyDown={event => { if (event.key === 'Enter' && (event.ctrlKey || event.metaKey) && !event.nativeEvent.isComposing) { event.preventDefault(); void ask() } }} /><button className="ai-button primary" type="submit" disabled={chatBusy || busy || !question.trim()} aria-label="Ask Profile AI">{chatBusy ? <Loader2 size={17} className="ai-spin" /> : <ArrowUp size={17} />}</button></form>
      </aside>
    </div>
    {citation && <Dialog title={citation.filename} onClose={() => setCitation(null)}><div className="pa-dialog-body">{citation.page_number != null && <p className="pa-caption">Page {citation.page_number}</p>}<pre className="pa-source-text">{citation.snippet}</pre></div></Dialog>}
    {dialog && <Dialog title={dialog === 'profile' ? 'Edit your profile' : dialog === 'project' ? 'Add a project' : dialog === 'skill' ? 'Review and add a skill' : 'Delete your saved resume?'} onClose={() => setDialog(null)} busy={busy}>
      {dialog === 'delete' ? <div className="pa-dialog-body"><p>This removes your saved resumes and their extracted analysis. Your profile skills and projects stay saved.</p>{formError && <Notice>{formError}</Notice>}<div className="pa-dialog-actions"><button className="ai-button secondary" disabled={busy} onClick={() => setDialog(null)}>Keep resume</button><button className="ai-button primary" disabled={busy} onClick={() => void mutate(() => api.deleteResume(), 'Resume and extracted analysis deleted.')}>Delete resume</button></div></div> : <form className="pa-dialog-body" onSubmit={saveForm}>{formError && <Notice>{formError}</Notice>}
        {dialog === 'profile' && <>{profileFields.map(([key, label]) => <label className="pa-field" key={key}>{label}<input type={key.endsWith('_url') ? 'url' : 'text'} maxLength={key.endsWith('_url') ? 500 : 150} value={form[key] || ''} onChange={event => setForm({ ...form, [key]: event.target.value })} /></label>)}<label className="pa-field">About you<textarea rows={3} maxLength={3000} value={form.summary || ''} onChange={event => setForm({ ...form, summary: event.target.value })} /></label></>}
        {dialog === 'skill' && <><p className="pa-caption">Confirm that this describes your experience. It will be saved as a self-reported skill.</p><label className="pa-field">Skill name<input required maxLength={150} value={form.name || ''} onChange={event => setForm({ ...form, name: event.target.value })} /></label><label className="pa-field">Your proficiency<select value={form.proficiency_level} onChange={event => setForm({ ...form, proficiency_level: event.target.value })}>{['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT'].map(level => <option key={level}>{level}</option>)}</select></label></>}
        {dialog === 'project' && <><label className="pa-field">Project title<input required maxLength={200} value={form.title || ''} onChange={event => setForm({ ...form, title: event.target.value })} /></label><label className="pa-field">Your contribution<textarea required rows={4} maxLength={6000} value={form.description || ''} onChange={event => setForm({ ...form, description: event.target.value })} /></label><label className="pa-field">Technologies, comma separated<input maxLength={1000} value={form.technologies || ''} onChange={event => setForm({ ...form, technologies: event.target.value })} /></label><label className="pa-field">Repository or demo URL<input type="url" maxLength={500} value={form.project_url || ''} onChange={event => setForm({ ...form, project_url: event.target.value })} /></label></>}
        <div className="pa-dialog-actions"><button type="button" className="ai-button secondary" disabled={busy} onClick={() => setDialog(null)}>Cancel</button><button type="submit" className="ai-button primary" disabled={busy}>{busy && <Loader2 size={15} className="ai-spin" />}{busy ? 'Saving…' : 'Save changes'}</button></div>
      </form>}
    </Dialog>}
  </section>
}
