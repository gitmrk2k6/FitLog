import { expect, test } from '@playwright/test'

import {
  TEST_PASSWORD,
  registerViaApi,
  testEmail,
  testId,
  testUsername,
} from '../helpers/user'

const TTFB_LIMIT = 2000
const FCP_LIMIT = 2000
const NAV_LIMIT = 3000

let sharedEmail: string

test.beforeAll(async () => {
  const id = testId()
  sharedEmail = testEmail(id)
  await registerViaApi(sharedEmail, testUsername(id), TEST_PASSWORD)
})

async function measureFcp(page: import('@playwright/test').Page): Promise<number> {
  return page.evaluate(() => {
    const entries = performance.getEntriesByType('paint')
    const fcp = entries.find((e) => e.name === 'first-contentful-paint')
    return fcp?.startTime ?? Infinity
  })
}

test.describe('ブラウザパフォーマンス計測', () => {
  test('ログインページ TTFB が 2000ms 以内', async ({ page }) => {
    await page.goto('/')
    const ttfb = await page.evaluate(() => {
      const [nav] = performance.getEntriesByType(
        'navigation',
      ) as PerformanceNavigationTiming[]
      return nav.responseStart - nav.requestStart
    })
    console.log(`Login TTFB: ${ttfb.toFixed(1)}ms`)
    expect(ttfb).toBeLessThan(TTFB_LIMIT)
  })

  test('ログインページ FCP が 2000ms 以内', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('button:has-text("ログイン")')
    const fcp = await measureFcp(page)
    console.log(`Login FCP: ${fcp.toFixed(1)}ms`)
    expect(fcp).toBeLessThan(FCP_LIMIT)
  })

  test('ログイン操作からダッシュボード到達が 3000ms 以内', async ({ page }) => {
    await page.goto('/')
    const start = Date.now()
    await page.fill('input[type="email"]', sharedEmail)
    await page.fill('input[type="password"]', TEST_PASSWORD)
    await page.click('button:has-text("ログイン")')
    await page.waitForURL('/dashboard')
    const elapsed = Date.now() - start
    console.log(`Login → Dashboard: ${elapsed}ms`)
    expect(elapsed).toBeLessThan(NAV_LIMIT)
  })

  test('ダッシュボード初期ロードが 3000ms 以内', async ({ page }) => {
    await page.goto('/')
    await page.fill('input[type="email"]', sharedEmail)
    await page.fill('input[type="password"]', TEST_PASSWORD)
    await page.click('button:has-text("ログイン")')
    await page.waitForURL('/dashboard')

    const start = Date.now()
    await page.reload()
    await page.waitForSelector('h2:has-text("ストリーク")')
    const elapsed = Date.now() - start
    console.log(`Dashboard reload: ${elapsed}ms`)
    expect(elapsed).toBeLessThan(NAV_LIMIT)
  })

  test('ワークアウト一覧 FCP が 2000ms 以内', async ({ page }) => {
    await page.goto('/')
    await page.fill('input[type="email"]', sharedEmail)
    await page.fill('input[type="password"]', TEST_PASSWORD)
    await page.click('button:has-text("ログイン")')
    await page.waitForURL('/dashboard')

    await page.goto('/list')
    await page.waitForSelector('h1:has-text("記録一覧")')
    const fcp = await measureFcp(page)
    console.log(`Workout list FCP: ${fcp.toFixed(1)}ms`)
    expect(fcp).toBeLessThan(FCP_LIMIT)
  })
})
