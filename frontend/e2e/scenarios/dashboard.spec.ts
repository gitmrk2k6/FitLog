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

test.describe('F-07/F-08/F-09 ダッシュボード・目標・ストリーク・PR', () => {
  test('ダッシュボード: ログイン直後に各セクションが表示される', async ({ page }) => {
    const id = testId()
    const email = testEmail(id)
    await registerViaApi(email, testUsername(id), TEST_PASSWORD)
    await loginViaUi(page, email, TEST_PASSWORD)

    await expect(page.locator('h2:has-text("目標達成率")')).toBeVisible()
    await expect(page.locator('h2:has-text("ストリーク")')).toBeVisible()
    await expect(page.locator('h2:has-text("記録ヒートマップ")')).toBeVisible()
    await expect(page.locator('h2:has-text("自己ベスト")')).toBeVisible()
  })

  test('目標設定: 週間目標を保存して現在の目標一覧に反映される', async ({ page }) => {
    const id = testId()
    const email = testEmail(id)
    await registerViaApi(email, testUsername(id), TEST_PASSWORD)
    await loginViaUi(page, email, TEST_PASSWORD)

    await page.goto('/goal')
    await page.waitForSelector('button:has-text("保存")')

    await page.selectOption('select:nth-of-type(1)', 'weekly')
    await page.selectOption('select:nth-of-type(2)', 'sessions')
    await page.fill('input[type="number"]', '3')
    await page.click('button:has-text("保存")')

    await expect(page.locator('.toast')).toBeVisible()
    await expect(page.locator('text=週間 / 実施回数')).toBeVisible()
    await expect(page.locator('text=3')).toBeVisible()
  })

  test('ストリーク: ワークアウト記録後にストリークが 1 になる', async ({ page }) => {
    const id = testId()
    const email = testEmail(id)
    await registerViaApi(email, testUsername(id), TEST_PASSWORD)
    const token = await loginViaApi(email, TEST_PASSWORD)
    const exerciseId = await getFirstExerciseId(token)
    await createWorkoutViaApi(token, exerciseId)

    await loginViaUi(page, email, TEST_PASSWORD)
    await page.goto('/dashboard')
    await page.waitForSelector('h2:has-text("ストリーク")')

    await expect(page.locator('.big')).toContainText('1')
  })

  test('PR: ワークアウト記録後に自己ベストセクションに種目が表示される', async ({ page }) => {
    const id = testId()
    const email = testEmail(id)
    await registerViaApi(email, testUsername(id), TEST_PASSWORD)
    const token = await loginViaApi(email, TEST_PASSWORD)
    const exerciseId = await getFirstExerciseId(token)
    await createWorkoutViaApi(token, exerciseId)

    await loginViaUi(page, email, TEST_PASSWORD)
    await page.goto('/dashboard')
    await page.waitForSelector('h2:has-text("自己ベスト")')

    await expect(page.locator('.pr-cell').first()).toBeVisible()
    await expect(page.locator('text=60 kg')).toBeVisible()
  })
})
