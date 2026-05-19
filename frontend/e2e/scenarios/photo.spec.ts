import { expect, test } from '@playwright/test'

import {
  TEST_PASSWORD,
  createWorkoutViaApi,
  getFirstExerciseId,
  loginViaApi,
  loginViaUi,
  registerViaApi,
  testEmail,
  testId,
  testUsername,
} from '../helpers/user'

const API = 'http://localhost:8000'

// 1×1 ピクセルの PNG（Base64）
const MINIMAL_PNG = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
  'base64',
)

test.describe('F-10 写真アップロード', () => {
  test('記録入力フォームに写真セクションが表示される', async ({ page }) => {
    const id = testId()
    const email = testEmail(id)
    await registerViaApi(email, testUsername(id), TEST_PASSWORD)
    await loginViaUi(page, email, TEST_PASSWORD)

    await page.goto('/record')
    await page.waitForSelector('text=写真（任意）')

    await expect(page.locator('text=写真（任意）')).toBeVisible()
    await expect(page.locator('input[type="file"]')).toBeVisible()
  })

  test('写真 API: バックエンドが PNG アップロードを受け付ける', async ({ page }) => {
    const id = testId()
    const email = testEmail(id)
    await registerViaApi(email, testUsername(id), TEST_PASSWORD)
    const token = await loginViaApi(email, TEST_PASSWORD)
    const exerciseId = await getFirstExerciseId(token)
    const workout = await createWorkoutViaApi(token, exerciseId)

    const res = await page.request.put(
      `${API}/workouts/${workout.id}/photo`,
      {
        headers: { Authorization: `Bearer ${token}` },
        multipart: {
          file: {
            name: 'test.png',
            mimeType: 'image/png',
            buffer: MINIMAL_PNG,
          },
        },
      },
    )

    expect(res.status()).toBe(200)
    const body = await res.json() as { photo_url: string }
    expect(body.photo_url).toBeTruthy()
  })

  test('写真 API: 写真を削除すると photo_url が null になる', async ({ page }) => {
    const id = testId()
    const email = testEmail(id)
    await registerViaApi(email, testUsername(id), TEST_PASSWORD)
    const token = await loginViaApi(email, TEST_PASSWORD)
    const exerciseId = await getFirstExerciseId(token)
    const workout = await createWorkoutViaApi(token, exerciseId)

    // アップロード
    await page.request.put(`${API}/workouts/${workout.id}/photo`, {
      headers: { Authorization: `Bearer ${token}` },
      multipart: {
        file: { name: 'test.png', mimeType: 'image/png', buffer: MINIMAL_PNG },
      },
    })

    // 削除
    const deleteRes = await page.request.delete(
      `${API}/workouts/${workout.id}/photo`,
      { headers: { Authorization: `Bearer ${token}` } },
    )
    expect(deleteRes.status()).toBe(200)
    const body = await deleteRes.json() as { photo_url: null }
    expect(body.photo_url).toBeNull()
  })
})
