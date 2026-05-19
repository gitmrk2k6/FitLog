import type { Page } from '@playwright/test'

const API = 'http://localhost:8000'

export function testId(): number {
  return Date.now()
}

export function testEmail(id: number): string {
  return `test_${id}@example.com`
}

export function testUsername(id: number): string {
  return `testuser_${id}`
}

export const TEST_PASSWORD = 'Password1'

export async function registerViaApi(
  email: string,
  username: string,
  password: string,
): Promise<{ id: number; email: string; username: string }> {
  const res = await fetch(`${API}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, username, password }),
  })
  if (!res.ok) throw new Error(`Register failed: ${await res.text()}`)
  return res.json()
}

export async function loginViaApi(email: string, password: string): Promise<string> {
  const res = await fetch(`${API}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) throw new Error(`Login failed: ${await res.text()}`)
  const data = await res.json() as { access_token: string }
  return data.access_token
}

export async function loginViaUi(page: Page, email: string, password: string): Promise<void> {
  await page.goto('/')
  await page.fill('input[type="email"]', email)
  await page.fill('input[type="password"]', password)
  await page.click('button:has-text("ログイン")')
  await page.waitForURL('**/dashboard')
}

export async function getFirstExerciseId(token: string): Promise<number> {
  const res = await fetch(`${API}/exercises`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error('Get exercises failed')
  const exercises = await res.json() as Array<{ id: number }>
  if (exercises.length === 0) throw new Error('No exercises found')
  return exercises[0].id
}

export async function createWorkoutViaApi(
  token: string,
  exerciseId: number,
  date: string = new Date().toISOString().slice(0, 10),
): Promise<{ id: number }> {
  const res = await fetch(`${API}/workouts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      performed_on: date,
      memo: 'E2Eテスト用ワークアウト',
      exercises: [
        { exercise_id: exerciseId, sets: [{ weight_kg: 60, reps: 10 }] },
      ],
    }),
  })
  if (!res.ok) throw new Error(`Create workout failed: ${await res.text()}`)
  return res.json()
}
