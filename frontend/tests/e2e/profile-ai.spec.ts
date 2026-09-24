import { expect, test, type Page } from '@playwright/test'

const resumeAnalysis = {
  skills: [{ name: 'Python', evidence: { chunk_id: 'resume-chunk', page_number: 1, quote: 'Built Python APIs for 200 users.' } }],
  sections: { projects: [{ text: 'Built Python APIs for 200 users.', page_number: 1 }] },
  links: [{ url: 'https://github.com/example/api', chunk_id: 'resume-chunk', page_number: 1 }],
  word_count: 220, page_count: 1, warnings: [],
  quality: { passed: 1, total: 2, note: 'Text-based checks, not an ATS vendor score or a hiring prediction.', checks: [
    { id: 'readable', label: 'Readable document text', passed: true, detail: '220 words extracted.' },
    { id: 'outcomes', label: 'Quantified outcomes', passed: false, detail: 'Describe a measurable result where accurate.' },
  ] },
}
const initial = {
  version: 'version-one',
  profile: { first_name: 'Ananya', last_name: 'Sen', degree: 'B.Tech', institution_name: 'Example College' },
  skills: [{ id: 'skill-one', name: 'Docker', proficiency_level: 'INTERMEDIATE', source: 'SELF', score: null }],
  projects: [{ id: 'project-one', title: 'Campus API', description: 'An API for student resources.', technologies: ['Python', 'FastAPI'], project_url: 'https://github.com/example/api', status: 'COMPLETED' }],
  certifications: [], internships: [], achievements: [],
  resume: { id: 'resume-one', filename: 'Ananya-resume.pdf', status: 'READY', updated_at: '2026-09-19T10:00:00Z', error: null, analysis: resumeAnalysis },
  documents: [{ id: 'document-one', filename: 'Architecture.pdf', status: 'READY', chunk_count: 2 }],
  suggested_skills: resumeAnalysis.skills, profile_only_skills: ['Docker'],
  summary: ['B.Tech at Example College.', 'Profile skills: Docker.', 'One saved project with Python and FastAPI.'],
  improvement_summary: ['Python is mentioned in the resume.', 'Docker is recorded in the profile but not found in the resume.', 'Add relevant project evidence where accurate.'],
}
const source = { index: 1, document_id: 'profile', filename: 'Profile · Skills', chunk_id: 'skills', snippet: 'Docker is self-reported at intermediate level.', similarity_score: 1 }
const matchResult = {
  version: 'version-one', target: { title: 'Your job description', required_skills: ['Python', 'Docker', 'SQL'], requirements_origin: 'user_confirmed' },
  resume_coverage: { found: 1, total: 3, percent: 33 }, profile_coverage: { found: 1, total: 3 },
  requirements: [
    { skill: 'Python', resume_status: 'found', profile_status: 'not_recorded', profile_evidence: [], resume_evidence: resumeAnalysis.skills[0].evidence },
    { skill: 'Docker', resume_status: 'not_found', profile_status: 'recorded', profile_evidence: ['Docker'], resume_evidence: null },
    { skill: 'SQL', resume_status: 'not_found', profile_status: 'not_recorded', profile_evidence: [], resume_evidence: null },
  ],
  note: 'Explicit skill keyword coverage only. Not an ATS score or hiring prediction.',
  requirements_note: 'Coverage uses the explicit required skills supplied for this target.',
  summary: ['1 of 3 skills found in the resume.', 'Docker and SQL were not found.', 'Add truthful project evidence.'],
  resources: [{ id: 'resource-one', title: 'SQL Practice', url: 'https://example.com/sql', provider: 'Catalog', skills: ['SQL'], is_free: true }],
  project_suggestions: [{ title: 'Build a small project using SQL', skill: 'SQL', description: 'Implement a project and write a README.' }],
}

async function setup(page: Page) {
  await page.addInitScript(() => {
    localStorage.setItem('access_token', 'ui-test-token')
    localStorage.setItem('user', JSON.stringify({ id: 'profile-owner', email: 'profile@example.com', role: 'STUDENT' }))
  })
  await page.route('**/api/v1/**', route => {
    const path = new URL(route.request().url()).pathname
    if (path.endsWith('/organizations')) return route.fulfill({ json: [] })
    if (path.endsWith('/health')) return route.fulfill({ json: { success: true, data: { status: 'ok' } } })
    if (path.endsWith('/models')) return route.fulfill({ json: { success: true, data: ['openai', 'claude', 'gemini'].map(provider => ({ provider, model: provider + '-test', is_configured: true })) } })
    if (path.endsWith('/profile-intelligence')) return route.fulfill({ json: { success: true, data: structuredClone(initial) } })
    return route.fulfill({ json: { success: true, data: [] } })
  })
}
test.beforeEach(async ({ page }) => setup(page))

test('saved profile, reviewed skill addition, and cited provider-free shortcut', async ({ page }) => {
  let state = structuredClone(initial)
  let additions = 0
  await page.route('**/profile-intelligence', route => route.fulfill({ json: { success: true, data: state } }))
  await page.route('**/students/me/skills', route => {
    additions++
    expect(route.request().postDataJSON()).toEqual({ name: 'Python', proficiency_level: 'INTERMEDIATE' })
    state = { ...state, version: 'version-two', suggested_skills: [], skills: [...state.skills, { id: 'skill-two', name: 'Python', proficiency_level: 'INTERMEDIATE', source: 'SELF', score: null }] }
    return route.fulfill({ status: 201, json: { success: true, data: {} } })
  })
  await page.route('**/profile-intelligence/chat', route => {
    expect(route.request().postDataJSON().question).toBe('List all my skills')
    return route.fulfill({ json: { success: true, data: { version: state.version, answers: [{ provider: 'profile', model: 'Saved profile facts', status: 'SUCCESS', answer: 'Your profile records Docker and Python [1].', sources: [source], latency_ms: 0 }] } } })
  })
  await page.setViewportSize({ width: 1440, height: 1050 })
  await page.goto('/ai-assistant?tab=profile')
  await expect(page.getByRole('heading', { name: 'Ananya Sen' })).toBeVisible()
  await expect(page.getByText('Ananya-resume.pdf', { exact: true })).toBeVisible()
  await page.locator('.pa-suggestion-chips').getByRole('button', { name: 'Python' }).click()
  expect(additions).toBe(0)
  await page.getByLabel('Your proficiency').selectOption('INTERMEDIATE')
  await page.getByRole('button', { name: 'Save changes' }).click()
  await expect(page.getByText('Skill added as self-reported.')).toBeVisible()
  expect(additions).toBe(1)
  await page.getByRole('button', { name: 'List all my skills' }).click()
  await expect(page.getByText('Your profile records Docker and Python', { exact: false })).toBeVisible()
  await page.getByRole('button', { name: 'View source 1: Profile · Skills' }).click()
  await expect(page.getByRole('dialog').getByText(source.snippet)).toBeVisible()
  await page.keyboard.press('Escape')
  await page.screenshot({ path: 'test-results/profile-ai-desktop.png', fullPage: true, animations: 'disabled' })
})

test('resume upload uses the profile endpoint and polls until analysis is ready', async ({ page }) => {
  let uploaded = false
  let readsAfterUpload = 0
  await page.route('**/profile-intelligence', route => {
    const state = structuredClone(initial)
    if (!uploaded) Object.assign(state, { resume: null, suggested_skills: [], profile_only_skills: [] })
    else {
      readsAfterUpload++
      if (readsAfterUpload === 1) Object.assign(state.resume, { status: 'PENDING', analysis: null })
      state.version = 'upload-' + Math.min(readsAfterUpload, 2)
    }
    return route.fulfill({ json: { success: true, data: state } })
  })
  await page.route('**/students/me/resume', route => {
    expect(route.request().method()).toBe('POST')
    expect(new URL(route.request().url()).search).toBe('')
    expect(route.request().headers()['content-type']).toContain('multipart/form-data')
    uploaded = true
    return route.fulfill({ status: 201, json: { success: true, data: {} } })
  })
  await page.goto('/ai-assistant?tab=profile')
  await expect(page.getByText('No resume saved', { exact: true })).toBeVisible()
  await page.getByLabel('Upload profile resume').setInputFiles({ name: 'resume.docx', mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', buffer: Buffer.from('mocked file') })
  await expect(page.getByText('Analyzing resume', { exact: true })).toBeVisible()
  await expect(page.getByText('Analysis ready', { exact: true })).toBeVisible({ timeout: 10000 })
  await page.getByRole('button', { name: 'Resume review', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Resume quality checklist' })).toBeVisible()
})

test('job match keeps profile evidence separate and clears an outdated result', async ({ page }) => {
  await page.route('**/profile-intelligence/job-match', route => {
    expect(route.request().postDataJSON()).toEqual({ job_description: 'Python, Docker and SQL are required for this role.', required_skills: ['Python', 'Docker', 'SQL'] })
    return route.fulfill({ json: { success: true, data: matchResult } })
  })
  await page.goto('/ai-assistant?tab=profile')
  await page.getByRole('button', { name: 'Job match', exact: true }).click()
  await page.getByRole('textbox', { name: 'Job description', exact: true }).fill('Python, Docker and SQL are required for this role.')
  await page.getByLabel('Required skills (optional, comma separated)').fill('Python, Docker, SQL')
  await page.getByRole('button', { name: 'Compare job requirements' }).click()
  await expect(page.getByText('33%', { exact: true })).toBeVisible()
  const row = page.getByRole('row').filter({ hasText: 'Docker' })
  await expect(row).toContainText('not found')
  await expect(row).toContainText('recorded')
  await expect(page.getByRole('link', { name: /SQL Practice/ })).toHaveAttribute('href', 'https://example.com/sql')
  await page.getByRole('textbox', { name: 'Job description', exact: true }).fill('A new job requires Kubernetes and Linux.')
  await expect(page.getByText('33%', { exact: true })).toHaveCount(0)
})

test('project chat sends the selected project and supporting document with model comparison', async ({ page }) => {
  await page.route('**/profile-intelligence/chat', route => {
    const body = route.request().postDataJSON()
    expect(body.scope).toBe('project')
    expect(body.project_id).toBe('project-one')
    expect(body.document_id).toBe('document-one')
    expect(body.compare).toBe(true)
    return route.fulfill({ json: { success: true, data: { version: initial.version, answers: [
      { provider: 'gemini', model: 'Gemini test', status: 'SUCCESS', answer: 'The selected project is Campus API [1].', sources: [{ ...source, filename: 'Project · Campus API' }], latency_ms: 10 },
      { provider: 'openai', model: 'OpenAI test', status: 'ERROR', error_message: 'Provider unavailable.', answer: '', sources: [], latency_ms: 0 },
    ] } } })
  })
  await page.goto('/ai-assistant?tab=profile')
  await page.getByRole('button', { name: 'Discuss this project' }).click()
  await page.getByLabel('Supporting document').selectOption('document-one')
  await page.getByLabel('Compare all three models with the same context').check()
  await page.getByLabel('Profile question').fill('Explain my contribution.')
  await page.getByRole('button', { name: 'Ask Profile AI' }).click()
  await expect(page.getByText('The selected project is Campus API', { exact: false })).toBeVisible()
  await expect(page.getByText('Provider unavailable.', { exact: true })).toBeVisible()
  await page.getByRole('combobox', { name: 'Model', exact: true }).selectOption('claude')
  await expect(page.getByText('The selected project is Campus API', { exact: false })).toHaveCount(0)
})

test('resume deletion requires confirmation and removes stale analysis', async ({ page }) => {
  let deleted = false
  await page.route('**/profile-intelligence', route => route.fulfill({ json: { success: true, data: deleted ? { ...initial, version: 'deleted', resume: null, suggested_skills: [], profile_only_skills: [] } : initial } }))
  await page.route('**/students/me/resume', route => {
    expect(route.request().method()).toBe('DELETE')
    deleted = true
    return route.fulfill({ status: 204 })
  })
  await page.goto('/ai-assistant?tab=profile')
  await page.getByRole('button', { name: 'Delete saved resume' }).click()
  await page.getByRole('button', { name: 'Keep resume' }).click()
  expect(deleted).toBe(false)
  await page.getByRole('button', { name: 'Delete saved resume' }).click()
  await page.getByRole('button', { name: 'Delete resume', exact: true }).click()
  await expect(page.getByText('No resume saved', { exact: true })).toBeVisible()
  await expect(page.getByText('Ananya-resume.pdf', { exact: true })).toHaveCount(0)
  await expect(page.locator('.pa-skills').getByText('Docker', { exact: true })).toBeVisible()
})

test('profile loading failure can be retried and the mobile layout does not overflow', async ({ page }) => {
  let fail = true
  await page.route('**/profile-intelligence', route => fail ? route.abort() : route.fulfill({ json: { success: true, data: initial } }))
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/ai-assistant?tab=profile')
  await expect(page.getByRole('alert')).toContainText('Cannot reach the server')
  fail = false
  await page.getByRole('button', { name: 'Try again' }).click()
  await expect(page.getByRole('heading', { name: 'Ananya Sen' })).toBeVisible()
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390)
  await page.screenshot({ path: 'test-results/profile-ai-mobile.png', fullPage: true, animations: 'disabled' })
})

test('skill learning is labeled without resume citations and an unrelated follow-up is redirected', async ({ page }) => {
  const knowledgeNote = 'General learning guidance about a recorded topic. This answer is not evidence from your resume or documents.'
  const explanation = 'Python was created by Guido van Rossum.'
  await page.route('**/profile-intelligence/chat', route => {
    const body = route.request().postDataJSON()
    expect(body.scope).toBe('profile')
    const learning = body.question === 'Who created Python?'
    if (!learning) {
      expect(body.question).toBe('Give me a paneer recipe.')
      expect(body.conversation_history).toEqual([
        { role: 'user', content: 'Who created Python?' },
        { role: 'assistant', content: explanation },
      ])
    }
    return route.fulfill({ json: { success: true, data: { version: initial.version, answers: [{
      provider: learning ? 'gemini' : 'profile', model: learning ? 'Gemini test' : 'Profile guide',
      status: 'SUCCESS', answer_kind: learning ? 'skill_learning' : 'out_of_scope',
      topic: learning ? 'Python' : null, knowledge_note: learning ? knowledgeNote : null,
      answer: learning ? explanation : 'Please focus on your recorded skills or use Continuous Chat for general questions.',
      sources: [], latency_ms: 10,
    }] } } })
  })
  await page.goto('/ai-assistant?tab=profile')
  await page.getByLabel('Profile question').fill('Who created Python?')
  await page.getByRole('button', { name: 'Ask Profile AI' }).click()
  const learning = page.locator('.pa-chat-answer').first()
  await expect(learning.getByText('Skill learning · Python', { exact: true })).toBeVisible()
  await expect(learning.getByText(knowledgeNote, { exact: true })).toBeVisible()
  await expect(learning.getByText(explanation, { exact: true })).toBeVisible()
  await expect(learning.locator('.pa-citations')).toHaveCount(0)
  await page.getByLabel('Profile question').fill('Give me a paneer recipe.')
  await page.getByRole('button', { name: 'Ask Profile AI' }).click()
  const redirect = page.locator('.pa-chat-answer').last()
  await expect(redirect.getByText('Please focus on your recorded skills or use Continuous Chat for general questions.')).toBeVisible()
  await expect(redirect.locator('.pa-learning-context')).toHaveCount(0)
  await expect(redirect.locator('.pa-citations')).toHaveCount(0)
  await page.screenshot({ path: 'test-results/profile-ai-learning.png', fullPage: true, animations: 'disabled' })
})

test('resume-only scope clears learning context and displays actual source citations', async ({ page }) => {
  await page.route('**/profile-intelligence/chat', route => {
    const body = route.request().postDataJSON()
    expect(body.conversation_history).toEqual([])
    const learning = body.scope === 'profile'
    return route.fulfill({ json: { success: true, data: { version: initial.version, answers: [{
      provider: 'gemini', model: 'Gemini test', status: 'SUCCESS',
      answer_kind: learning ? 'skill_learning' : 'profile',
      topic: learning ? 'Python' : null, knowledge_note: learning ? 'General knowledge, not resume evidence.' : null,
      answer: learning ? 'Python was created by Guido van Rossum.' : 'Your resume mentions Python but does not describe its history [1].',
      sources: learning ? [] : [{ ...source, filename: 'Resume · Ananya-resume.pdf', snippet: 'Built Python APIs for 200 users.' }], latency_ms: 10,
    }] } } })
  })
  await page.goto('/ai-assistant?tab=profile')
  await page.getByLabel('Profile question').fill('Who created Python?')
  await page.getByRole('button', { name: 'Ask Profile AI' }).click()
  await expect(page.getByText('Skill learning · Python', { exact: true })).toBeVisible()
  await page.getByRole('combobox', { name: 'Sources', exact: true }).selectOption('resume')
  await expect(page.getByText('Skill learning · Python', { exact: true })).toHaveCount(0)
  await expect(page.getByText('Answers use only the selected evidence. Click a citation to inspect its source.')).toBeVisible()
  await page.getByLabel('Profile question').fill('Who created Python?')
  await page.getByRole('button', { name: 'Ask Profile AI' }).click()
  await page.getByRole('button', { name: 'View source 1: Resume · Ananya-resume.pdf' }).click()
  await expect(page.getByRole('dialog').getByText('Built Python APIs for 200 users.', { exact: true })).toBeVisible()
})

test('subject links are visible without a job and study notes open a scoped conversation', async ({ page }) => {
  await page.route('**/profile-intelligence', route => route.fulfill({ json: { success: true, data: {
    ...initial, learning_resources: [
      { id: 'python-course', title: 'Python Fundamentals', url: 'https://example.com/python', provider: 'Catalogue', skills: ['Python'], is_free: true },
    ],
  } } }))
  await page.route('**/profile-intelligence/chat', route => {
    const body = route.request().postDataJSON()
    expect(body.scope).toBe('documents')
    expect(body.document_id).toBe('document-one')
    expect(body.project_id).toBeUndefined()
    return route.fulfill({ json: { success: true, data: { version: initial.version, answers: [{
      provider: 'gemini', model: 'Gemini test', status: 'SUCCESS', answer_kind: 'profile',
      answer: 'The document describes the campus API [1].',
      sources: [{ ...source, document_id: 'document-one', filename: 'Architecture.pdf', snippet: 'The campus API serves student resources.' }],
      latency_ms: 10,
    }] } } })
  })
  await page.goto('/ai-assistant?tab=profile')
  const subjects = page.getByRole('article', { name: 'Subject and learning links' })
  await expect(subjects.getByRole('link', { name: /Python Fundamentals/ })).toHaveAttribute('href', 'https://example.com/python')
  await expect(subjects).toContainText('Website contents have not been fetched.')
  await subjects.getByRole('button', { name: 'Architecture.pdf', exact: true }).click()
  await expect(page.getByRole('combobox', { name: 'Sources', exact: true })).toHaveValue('documents')
  await expect(page.getByRole('combobox', { name: 'Supporting document', exact: true })).toHaveValue('document-one')
  await page.getByLabel('Profile question').fill('Explain the document.')
  await page.getByRole('button', { name: 'Ask Profile AI' }).click()
  await page.getByRole('button', { name: 'View source 1: Architecture.pdf' }).click()
  await expect(page.getByRole('dialog').getByText('The campus API serves student resources.', { exact: true })).toBeVisible()
})
