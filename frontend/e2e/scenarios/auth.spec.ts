import { expect, test } from '@playwright/test'

import {
  TEST_PASSWORD,
  loginViaUi,
  registerViaApi,
  testEmail,
  testId,
  testUsername,
} from '../helpers/user'

test.describe('F-01 認証', () => {
  test('新規登録: フォームから登録してログイン画面へ遷移する', async ({ page }) => {
    const id = testId()
    const email = testEmail(id)
    const username = testUsername(id)

    await page.goto('/signup')
    await page.fill('input[autocomplete="username"]', username)
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', TEST_PASSWORD)
    await page.click('button:has-text("登録する")')

    await page.waitForURL('/')
    await expect(page.locator('button:has-text("ログイン")')).toBeVisible()
  })

  test('ログイン: 正しい認証情報でダッシュボードへ遷移する', async ({ page }) => {
    const id = testId()
    const email = testEmail(id)
    await registerViaApi(email, testUsername(id), TEST_PASSWORD)

    await loginViaUi(page, email, TEST_PASSWORD)

    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('h2:has-text("ストリーク")')).toBeVisible()
  })

  test('ログイン失敗: 誤ったパスワードでエラーが表示される', async ({ page }) => {
    const id = testId()
    const email = testEmail(id)
    await registerViaApi(email, testUsername(id), TEST_PASSWORD)

    await page.goto('/')
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', 'WrongPass9')
    await page.click('button:has-text("ログイン")')

    await expect(page.locator('p.muted').filter({ hasText: /正しくありません/ })).toBeVisible()
    await expect(page).toHaveURL('/')
  })

  test('ログアウト: ログアウト後にログイン画面へ戻る', async ({ page }) => {
    const id = testId()
    const email = testEmail(id)
    await registerViaApi(email, testUsername(id), TEST_PASSWORD)
    await loginViaUi(page, email, TEST_PASSWORD)

    await page.click('button:has-text("ログアウト")')

    await page.waitForURL('/')
    await expect(page.locator('button:has-text("ログイン")')).toBeVisible()
  })
})
