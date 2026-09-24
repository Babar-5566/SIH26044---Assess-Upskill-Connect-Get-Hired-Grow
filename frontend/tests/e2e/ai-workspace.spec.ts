import { expect, test } from '@playwright/test'

const document = { id: 'guide-1', original_filename: 'Engineering-handbook.pdf', file_type: 'pdf', file_size_bytes: 124000, chunk_count: 3, status: 'READY', created_at: '' }
const source = { index: 1, document_id: document.id, filename: document.original_filename, page_number: 2, chunk_id: 'passage-1', snippet: 'The engineering team uses Python 3.10 and FastAPI. Every release requires a code review.', similarity_score: 0.91 }

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('access_token', 'ui-test-token')
    localStorage.setItem('user', JSON.stringify({ id: 'ui-test', email: 'review@example.com', role: 'STUDENT' }))
  })
  await page.route('**/api/v1/**', route => {
    const path = new URL(route.request().url()).pathname
    if (path.endsWith('/organizations')) return route.fulfill({ json: [] })
    if (path.endsWith('/health')) return route.fulfill({ json: { success: true, data: { status: 'ok' } } })
    if (path.endsWith('/models')) return route.fulfill({ json: { success: true, data: ['openai', 'claude', 'gemini'].map(provider => ({ provider, model: `${provider}-test`, is_configured: true })) } })
    return route.fulfill({ json: { success: true, data: [] } })
  })
})

test('document list connection failure can be retried without an upload error', async ({ page }) => {
  let fail = true
  await page.route('**/ai-assistant/documents', route => fail ? route.abort('failed') : route.fulfill({ json: { success: true, data: [document] } }))
  await page.goto('/ai-assistant')
  await page.getByRole('button', { name: 'Document RAG & Citations' }).click()
  await expect(page.getByRole('alert')).toContainText('Cannot reach the server')
  await expect(page.getByRole('button', { name: 'Choose file', exact: true })).toBeEnabled()
  fail = false
  await page.getByRole('button', { name: 'Try again' }).click()
  await expect(page.getByRole('button', { name: `Select ${document.original_filename}` })).toBeVisible()
  await expect(page.getByRole('alert')).toHaveCount(0)
})

test('drag-and-drop upload, formatted answer, citation dialog, and document deletion', async ({ page }) => {
  let uploaded = false
  let question: any
  await page.route('**/ai-assistant/documents', route => route.fulfill({ json: { success: true, data: uploaded ? [document] : [] } }))
  await page.route('**/ai-assistant/documents/upload', async route => {
    expect(route.request().headers()['content-type']).toContain('multipart/form-data; boundary=')
    uploaded = true
    await route.fulfill({ status: 201, json: { success: true, data: { document_id: document.id } } })
  })
  await page.route(`**/ai-assistant/documents/${document.id}`, route => {
    if (route.request().method() === 'DELETE') { uploaded = false; return route.fulfill({ json: { success: true, data: {} } }) }
    return route.fulfill({ json: { success: true, data: { ...document, chunks: [{ chunk_id: source.chunk_id, chunk_index: 0, page_number: 2, content: source.snippet }] } } })
  })
  await page.route('**/ai-assistant/rag/query', route => {
    question = route.request().postDataJSON()
    return route.fulfill({ json: { success: true, data: { query: question.question, answer: '## Team requirements\n\nUse **Python 3.10** and FastAPI [1].\n\n- Review every release.\n- Keep changes small.', sources: [source], status: 'SUCCESS', model_used: 'Gemini', latency_ms: 230, retrieved_chunks_count: 1 } } })
  })
  await page.setViewportSize({ width: 1440, height: 1000 })
  await page.goto('/ai-assistant')
  await page.getByRole('button', { name: 'Document RAG & Citations' }).click()
  await page.locator('.ai-dropzone').evaluate(element => {
    const data = new DataTransfer()
    data.items.add(new File(['Python requirements'], 'requirements.txt', { type: 'text/plain' }))
    element.dispatchEvent(new DragEvent('drop', { bubbles: true, dataTransfer: data }))
  })
  await expect(page.getByText('requirements.txt is ready to explore.')).toBeVisible()
  await expect(page.getByRole('button', { name: `Select ${document.original_filename}` })).toHaveAttribute('aria-pressed', 'true')
  await page.getByLabel('Document question').fill('What does the engineering team need?')
  await page.getByRole('button', { name: 'Query', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Team requirements' })).toBeVisible()
  expect(question.document_id).toBe(document.id)
  await expect(page.locator('.ai-answer strong')).toHaveText('Python 3.10')
  await page.screenshot({ path: 'test-results/ai-rag-desktop.png', fullPage: true, animations: 'disabled' })
  await page.getByRole('button', { name: `View source 1: ${document.original_filename}` }).click()
  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  await expect(dialog.getByText(source.snippet)).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(dialog).toHaveCount(0)
  await page.setViewportSize({ width: 390, height: 844 })
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390)
  await page.screenshot({ path: 'test-results/ai-rag-mobile.png', fullPage: true, animations: 'disabled' })
  await page.getByRole('button', { name: `Delete ${document.original_filename}` }).click()
  await expect(page.getByRole('dialog', { name: 'Delete this document?' })).toBeVisible()
  await page.getByRole('button', { name: 'Keep document' }).click()
  expect(uploaded).toBe(true)
  await page.getByRole('button', { name: `Delete ${document.original_filename}` }).click()
  await page.getByRole('button', { name: 'Delete document', exact: true }).click()
  await expect(page.getByRole('button', { name: `Select ${document.original_filename}` })).toHaveCount(0)
  await expect(page.getByRole('heading', { name: 'Team requirements' })).toHaveCount(0)
})

test('unsupported files are rejected before making an upload request', async ({ page }) => {
  let uploads = 0
  await page.route('**/ai-assistant/documents/upload', route => { uploads++; return route.abort() })
  await page.goto('/ai-assistant')
  await page.getByRole('button', { name: 'Document RAG & Citations' }).click()
  await page.getByLabel('Upload document', { exact: true }).setInputFiles({ name: 'script.exe', mimeType: 'application/octet-stream', buffer: Buffer.from('invalid') })
  await expect(page.getByRole('alert')).toContainText('Choose a PDF')
  expect(uploads).toBe(0)
})

test('model output renders markdown without executing raw HTML', async ({ page }) => {
  await page.route('**/ai-assistant/compare', route => route.fulfill({ json: { success: true, data: [{ provider: 'openai', model: 'test', status: 'SUCCESS', latency_ms: 120, content: '## A useful answer\n\n**Summary**\n\n<script>window.unsafeMarkup = true</script>\n\n```python\nprint("hello")\n```' }] } }))
  await page.goto('/ai-assistant')
  await page.getByLabel('Comparison question').fill('Explain this')
  await page.getByRole('button', { name: 'Compare Models Side-by-Side' }).click()
  await expect(page.getByRole('heading', { name: 'A useful answer' })).toBeVisible()
  await expect(page.locator('.ai-answer pre code')).toContainText('print("hello")')
  expect(await page.evaluate(() => (window as any).unsafeMarkup)).toBeUndefined()
})
