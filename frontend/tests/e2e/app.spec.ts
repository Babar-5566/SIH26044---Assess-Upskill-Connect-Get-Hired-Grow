import { expect, test } from '@playwright/test'

test('anonymous users are redirected to login', async ({ page }) => {
  await page.goto('/student/jobs')
  await expect(page).toHaveURL(/\/login$/)
  await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible()
})

test('student can login and access job workflow', async ({ page }) => {
  await page.route('**/api/v1/auth/login', route => route.fulfill({ json: { data: { access_token: 'test-token' } } }))
  await page.route('**/api/v1/auth/me', route => route.fulfill({ json: { data: { id: '1', email: 'student@example.com', role: 'STUDENT' } } }))
  await page.route('**/api/v1/organizations', route => route.fulfill({ json: [] }))
  await page.route('**/api/v1/jobs', route => route.fulfill({ json: [{ id: 'job-1', title: 'Junior Engineer', company_name: 'Acme', location: 'Remote' }] }))
  await page.goto('/login')
  await page.getByLabel(/email/i).fill('student@example.com')
  await page.getByLabel(/password/i).fill('StrongPass123')
  await page.getByRole('button', { name: /sign in/i }).click()
  await page.goto('/student/jobs')
  await expect(page.getByRole('heading', { name: /jobs/i })).toBeVisible()
  await expect(page.getByText('Junior Engineer')).toBeVisible()
})

test('student cannot open company management route', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('access_token', 'test-token')
    localStorage.setItem('user', JSON.stringify({ id: '1', email: 'student@example.com', role: 'STUDENT' }))
  })
  await page.goto('/company/internships')
  await expect(page).toHaveURL(/\/dashboard$/)
})
