import { expect, test } from '@playwright/test'

import {
  TEST_PASSWORD,
  loginViaUi,
  registerViaApi,
  testEmail,
  testId,
  testUsername,
} from '../helpers/user'

test.describe('F-02/F-03 ワークアウト記録・一覧・詳細', () => {
  test('記録入力: ワークアウトを保存して一覧に表示される', async ({ page }) => {
    const id = testId()
    const email = testEmail(id)
    await registerViaApi(email, testUsername(id), TEST_PASSWORD)
    await loginViaUi(page, email, TEST_PASSWORD)

    await page.goto('/record')
    await page.waitForSelector('button:has-text("保存")')
    await page.click('button:has-text("保存")')

    await page.waitForURL('/list')
    await expect(page.locator('.list-item')).toHaveCount(1)
  })

  test('記録一覧: 記録をクリックして詳細画面へ遷移する', async ({ page }) => {
    const id = testId()
    const email = testEmail(id)
    await registerViaApi(email, testUsername(id), TEST_PASSWORD)
    await loginViaUi(page, email, TEST_PASSWORD)

    await page.goto('/record')
    await page.waitForSelector('button:has-text("保存")')
    await page.click('button:has-text("保存")')
    await page.waitForURL('/list')

    await page.click('.list-item')

    await expect(page).toHaveURL(/\/list\/\d+/)
    await expect(page.locator('h1')).toContainText('の記録')
  })

  test('記録詳細: 総ボリューム・ナイストレ・アドバイスセクションが表示される', async ({ page }) => {
    const id = testId()
    const email = testEmail(id)
    await registerViaApi(email, testUsername(id), TEST_PASSWORD)
    await loginViaUi(page, email, TEST_PASSWORD)

    await page.goto('/record')
    await page.waitForSelector('button:has-text("保存")')
    await page.click('button:has-text("保存")')
    await page.waitForURL('/list')
    await page.click('.list-item')

    await expect(page.locator('text=総ボリューム')).toBeVisible()
    await expect(page.locator('h2:has-text("ナイストレーニング")')).toBeVisible()
    await expect(page.locator('h2:has-text("アドバイス")')).toBeVisible()
  })

  test('記録編集: 記録を編集して更新できる', async ({ page }) => {
    const id = testId()
    const email = testEmail(id)
    await registerViaApi(email, testUsername(id), TEST_PASSWORD)
    await loginViaUi(page, email, TEST_PASSWORD)

    await page.goto('/record')
    await page.waitForSelector('button:has-text("保存")')
    await page.click('button:has-text("保存")')
    await page.waitForURL('/list')
    await page.click('.list-item')

    await page.click('button:has-text("編集")')
    await expect(page).toHaveURL(/\/record\?id=\d+/)
    await page.fill('input[placeholder="調子・気づきなど"]', 'E2E編集テスト')
    await page.click('button:has-text("保存")')

    await page.waitForURL('/list')
    await expect(page.locator('.list-item')).toHaveCount(1)
  })
})
