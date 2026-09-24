import { expect, test } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('access_token', 'test-token')
    localStorage.setItem('user', JSON.stringify({ id: '1', email: 'student@example.com', role: 'STUDENT' }))
  })
  await page.route('**/api/v1/**', async route => {
    const url = new URL(route.request().url())
    if (url.pathname.endsWith('/organizations')) return route.fulfill({ json: [] })
    return route.fulfill({ json: { success: true, data: [] } })
  })
})

test('switching models and clearing a conversation preserves each model history', async ({ page }) => {
  const requests: any[] = []
  await page.route('**/ai-assistant/chat', async route => {
    const body = route.request().postDataJSON()
    requests.push(body)
    await route.fulfill({ json: { success: true, data: { provider: body.provider, model: body.provider, status: 'SUCCESS', content: `${body.provider} response ${requests.length}`, latency_ms: 1 } } })
  })
  await page.goto('/ai-assistant')
  await page.getByRole('button', { name: 'Continuous Chat' }).click()
  await page.getByPlaceholder('Message gemini...').fill('Gemini question')
  await page.getByRole('button', { name: 'Send message' }).click()
  await expect(page.getByText('gemini response 1', { exact: true })).toBeVisible()
  await page.getByLabel('Chat model').selectOption('openai')
  await expect(page.getByText('Gemini question', { exact: true })).not.toBeVisible()
  await page.getByPlaceholder('Message openai...').fill('OpenAI question')
  await page.getByRole('button', { name: 'Send message' }).click()
  await expect(page.getByText('openai response 2', { exact: true })).toBeVisible()
  expect(requests[1].conversation_history).toEqual([])
  await page.getByLabel('Chat model').selectOption('gemini')
  await expect(page.getByText('gemini response 1', { exact: true })).toBeVisible()
  await page.getByPlaceholder('Message gemini...').fill('Follow up')
  await page.getByRole('button', { name: 'Send message' }).click()
  await expect(page.getByText('gemini response 3', { exact: true })).toBeVisible()
  expect(requests[2].conversation_history).toEqual([
    { role: 'user', content: 'Gemini question' }, { role: 'assistant', content: 'gemini response 1' },
  ])
  await page.getByRole('button', { name: 'Clear Conversation' }).click()
  await expect(page.getByText('gemini response 3', { exact: true })).not.toBeVisible()
  await page.getByLabel('Chat model').selectOption('openai')
  await expect(page.getByText('openai response 2', { exact: true })).toBeVisible()
})

test('continue uses the compared question even after the input is edited', async ({ page }) => {
  await page.route('**/ai-assistant/compare', route => route.fulfill({ json: { success: true, data: [
    { provider: 'openai', model: 'test-model', content: 'Compared answer', status: 'SUCCESS', latency_ms: 1 },
  ] } }))
  await page.goto('/ai-assistant')
  await page.getByLabel('Comparison question').fill('Original question')
  await page.getByRole('button', { name: 'Compare Models Side-by-Side' }).click()
  await expect(page.getByText('Compared answer', { exact: true })).toBeVisible()
  await page.getByLabel('Comparison question').fill('Changed question')
  await page.getByRole('button', { name: 'Continue with OpenAI', exact: true }).click()
  await expect(page.getByText('Original question', { exact: true })).toBeVisible()
  await expect(page.getByText('Changed question', { exact: true })).not.toBeVisible()
})

test('failed chat restores the question and does not enter model history', async ({ page }) => {
  await page.route('**/ai-assistant/chat', route => route.fulfill({ json: { success: true, data: { status: 'ERROR', content: '', error_message: 'Provider temporarily unavailable' } } }))
  await page.goto('/ai-assistant')
  await page.getByRole('button', { name: 'Continuous Chat' }).click()
  await page.getByPlaceholder('Message gemini...').fill('Retry me')
  await page.getByRole('button', { name: 'Send message' }).click()
  await expect(page.getByRole('alert')).toHaveText('Provider temporarily unavailable')
  await expect(page.getByPlaceholder('Message gemini...')).toHaveValue('Retry me')
  await expect(page.getByText('Start a conversation with GEMINI')).toBeVisible()
})

test('document upload and RAG errors display the backend message', async ({ page }) => {
  await page.route('**/ai-assistant/documents/upload', route => route.fulfill({ status: 422, json: { success: false, error: { message: 'Document is password protected.' } } }))
  await page.route('**/ai-assistant/rag/query', route => route.fulfill({ json: { success: true, data: { status: 'ERROR', answer: '', error_message: 'Embedding service unavailable.' } } }))
  await page.goto('/ai-assistant')
  await page.getByRole('button', { name: 'Document RAG & Citations' }).click()
  await page.locator('input[type=file]').setInputFiles({ name: 'guide.txt', mimeType: 'text/plain', buffer: Buffer.from('Hello') })
  await expect(page.getByText('Document is password protected.')).toBeVisible()
  await page.getByPlaceholder(/Ask a question across/).fill('What is required?')
  await page.getByRole('button', { name: 'Query', exact: true }).click()
  await expect(page.getByText('Embedding service unavailable.', { exact: true })).toBeVisible()
})

test('assistant fits a mobile viewport and navigation is accessible', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/ai-assistant')
  await expect(page.getByRole('heading', { name: 'Multi-LLM & RAG Assistant.' })).toBeVisible()
  for (const tab of ['Multi-LLM Arena', 'Continuous Chat', 'Document RAG & Citations']) {
    await page.getByRole('button', { name: tab, exact: true }).click()
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390)
  }
  await page.getByRole('button', { name: 'Open navigation' }).click()
  await expect(page.getByRole('link', { name: 'Multi-LLM & RAG AI' })).toBeVisible()
})
