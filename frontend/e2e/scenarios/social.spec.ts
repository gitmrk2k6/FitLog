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

test.describe('F-04/F-05/F-06 フォロー・ナイストレ・アドバイス', () => {
  test('フォロー: ユーザー検索してフォローできる', async ({ page }) => {
    const idA = testId()
    const idB = idA + 1

    await registerViaApi(testEmail(idA), testUsername(idA), TEST_PASSWORD)
    await registerViaApi(testEmail(idB), testUsername(idB), TEST_PASSWORD)

    await loginViaUi(page, testEmail(idA), TEST_PASSWORD)
    await page.goto('/search')
    await page.fill('input[placeholder="ユーザー名で検索"]', testUsername(idB))
    await page.click('button:has-text("検索")')

    await expect(page.locator(`text=@${testUsername(idB)}`)).toBeVisible()
    await page.click('button:has-text("フォローする")')
    await expect(page.locator('button:has-text("フォロー中")')).toBeVisible()
  })

  test('フィード: フォロー後に相手のワークアウトがフィードに表示される', async ({ page }) => {
    const idA = testId()
    const idB = idA + 1

    await registerViaApi(testEmail(idA), testUsername(idA), TEST_PASSWORD)
    const userB = await registerViaApi(testEmail(idB), testUsername(idB), TEST_PASSWORD)

    // ユーザーB がワークアウトを作成
    const tokenB = await loginViaApi(testEmail(idB), TEST_PASSWORD)
    const exerciseId = await getFirstExerciseId(tokenB)
    await createWorkoutViaApi(tokenB, exerciseId)

    // ユーザーA が B をフォロー（実際の DB 上の user ID を使う）
    const tokenA = await loginViaApi(testEmail(idA), TEST_PASSWORD)
    await fetch(`${API}/users/${userB.id}/follow`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${tokenA}` },
    })

    await loginViaUi(page, testEmail(idA), TEST_PASSWORD)
    await page.goto('/feed')

    await expect(page.locator(`text=@${testUsername(idB)}`)).toBeVisible()
  })

  test('ナイストレ → アドバイス: フィードからナイストレしてアドバイスを投稿できる', async ({ page }) => {
    const idA = testId()
    const idB = idA + 1

    await registerViaApi(testEmail(idA), testUsername(idA), TEST_PASSWORD)
    const userB = await registerViaApi(testEmail(idB), testUsername(idB), TEST_PASSWORD)

    // ユーザーB のワークアウト作成
    const tokenB = await loginViaApi(testEmail(idB), TEST_PASSWORD)
    const exerciseId = await getFirstExerciseId(tokenB)
    const workout = await createWorkoutViaApi(tokenB, exerciseId)

    // ユーザーA が B をフォロー
    const tokenA = await loginViaApi(testEmail(idA), TEST_PASSWORD)
    await fetch(`${API}/users/${userB.id}/follow`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${tokenA}` },
    })

    await loginViaUi(page, testEmail(idA), TEST_PASSWORD)
    await page.goto('/feed')
    await page.waitForSelector(`text=@${testUsername(idB)}`)

    // ナイストレ
    const cheerBtn = page.locator('button').filter({ hasText: '👍 ナイストレ' }).first()
    await cheerBtn.click()
    await expect(page.locator('button').filter({ hasText: '👍 ナイストレ 1' })).toBeVisible()

    // 詳細へ → アドバイス投稿
    await page.goto(`/list/${workout.id}`)
    await page.fill('input[placeholder="応援コメントを送る（最大140文字）"]', 'E2Eテストのアドバイスです')
    await page.click('button:has-text("送信")')

    await expect(page.locator('text=E2Eテストのアドバイスです')).toBeVisible()
  })
})
