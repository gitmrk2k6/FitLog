/**
 * FitLog 全機能デモ動画 (F-01〜F-10)
 * npx playwright test --config demo.config.ts --headed
 */
import { test, expect, Page } from '@playwright/test'
import * as fs from 'fs'
import * as path from 'path'

const BASE = 'https://d20n2etaaqstlw.cloudfront.net'
const WAIT = (ms: number) => new Promise(r => setTimeout(r, ms))

// デモユーザー（毎実行ユニークにするためタイムスタンプ付き）
const TS = Date.now().toString().slice(-6)
const USER_A = {
  username: `tanaka_${TS}`,
  email: `tanaka${TS}@demo.example.com`,
  password: 'Demo1234',
}
const USER_B = {
  username: `suzuki_${TS}`,
  email: `suzuki${TS}@demo.example.com`,
  password: 'Demo1234',
}

// 最小 PNG (1x1 透明)
const PNG_PATH = path.resolve('/tmp/fitlog-demo-photo.png')
fs.writeFileSync(
  PNG_PATH,
  Buffer.from(
    '89504e470d0a1a0a0000000d494844520000000100000001080600000' +
    '01f15c4890000000a49444154789c6360000002000154a24f600000000049454e44ae426082',
    'hex',
  ),
)

// ─── ヘルパー ──────────────────────────────────────────────
async function login(page: Page, user: typeof USER_A) {
  await page.goto(`${BASE}/`)
  await WAIT(600)
  await page.fill('input[type="email"]', user.email)
  await WAIT(400)
  await page.fill('input[type="password"]', user.password)
  await WAIT(400)
  await page.click('button:has-text("ログイン")')
  await page.waitForURL(`${BASE}/dashboard`)
  await WAIT(1200)
}

async function logout(page: Page) {
  await page.click('button:has-text("ログアウト")')
  await page.waitForURL(`${BASE}/`)
  await WAIT(800)
}

// ─── メインテスト ───────────────────────────────────────────
test('FitLog 全機能デモ (F-01〜F-10)', async ({ page }) => {
  test.setTimeout(300_000)

  // ══════════════════════════════════════════
  // F-01: 新規登録
  // ══════════════════════════════════════════
  await page.goto(`${BASE}/`)
  await WAIT(1000)
  // ログイン画面を見せる
  await WAIT(1500)
  // 新規登録リンクをクリック
  await page.click('a:has-text("新規登録")')
  await WAIT(800)
  // フォーム入力
  await page.fill('input[placeholder="you"]', USER_A.username)
  await WAIT(400)
  await page.fill('input[placeholder="you@example.com"]', USER_A.email)
  await WAIT(400)
  await page.fill('input[type="password"]', USER_A.password)
  await WAIT(600)
  await page.click('button:has-text("登録する")')
  await page.waitForURL(`${BASE}/`)
  await WAIT(800)

  // F-01: ログイン
  await page.fill('input[type="email"]', USER_A.email)
  await WAIT(400)
  await page.fill('input[type="password"]', USER_A.password)
  await WAIT(400)
  await page.click('button:has-text("ログイン")')
  await page.waitForURL(`${BASE}/dashboard`)
  await WAIT(2000)

  // ══════════════════════════════════════════
  // F-02/F-03: ワークアウト記録（2種目・複数セット）
  // ══════════════════════════════════════════
  await page.click('a:has-text("記録")')
  await page.waitForURL(`${BASE}/record`)
  await WAIT(1000)

  // 種目1: ベンチプレス
  await page.locator('select').first().selectOption({ label: 'ベンチプレス' })
  await WAIT(500)
  // セット1: 80kg×5
  let inputs = await page.locator('input[type="number"]').all()
  await inputs[0].fill('80')
  await WAIT(300)
  await inputs[1].fill('5')
  await WAIT(300)
  // セット追加
  await page.locator('button:has-text("+ セット追加")').first().click()
  await WAIT(500)
  inputs = await page.locator('input[type="number"]').all()
  await inputs[2].fill('80')
  await WAIT(300)
  await inputs[3].fill('5')
  await WAIT(300)
  // セット追加
  await page.locator('button:has-text("+ セット追加")').first().click()
  await WAIT(500)
  inputs = await page.locator('input[type="number"]').all()
  await inputs[4].fill('75')
  await WAIT(300)
  await inputs[5].fill('8')
  await WAIT(300)

  // 種目2: スクワット追加
  await page.click('button:has-text("+ 種目を追加")')
  await WAIT(600)
  await page.locator('select').nth(1).selectOption({ label: 'スクワット' })
  await WAIT(500)
  inputs = await page.locator('input[type="number"]').all()
  await inputs[6].fill('100')
  await WAIT(300)
  await inputs[7].fill('5')
  await WAIT(300)

  // メモ（input 要素、textarea ではない）
  await page.fill('input[placeholder="調子・気づきなど"]', '今日は調子良し！')
  await WAIT(500)
  // 保存
  await page.click('button:has-text("保存")')
  await page.waitForURL(`${BASE}/list`)
  await WAIT(1200)

  // 記録一覧を見せる（list-item はクリックイベントで遷移）
  await WAIT(1500)

  // 記録詳細を開く（F-09: 自己ベスト更新🏅 を確認）
  await page.locator('.list-item').first().click()
  await page.waitForURL(/\/list\/\d+/)
  await WAIT(1500)
  await expect(page.locator('text=自己ベスト更新🏅').first()).toBeVisible()
  await WAIT(2000)

  // ══════════════════════════════════════════
  // F-10: 写真アップロード
  // ══════════════════════════════════════════
  const fileInput = page.locator('input[type="file"]')
  await fileInput.setInputFiles(PNG_PATH)
  await WAIT(3000)
  // 写真が表示されることを確認
  await WAIT(1000)

  // ══════════════════════════════════════════
  // F-07: 目標設定
  // ══════════════════════════════════════════
  await page.click('a:has-text("目標")')
  await page.waitForURL(`${BASE}/goal`)
  await WAIT(1000)
  // 週間・実施回数・4回に設定
  await page.locator('select').nth(0).selectOption({ label: '週間' })
  await WAIT(400)
  await page.locator('select').nth(1).selectOption({ label: '実施回数' })
  await WAIT(400)
  const goalInput = page.locator('input[type="number"]')
  await goalInput.fill('4')
  await WAIT(400)
  await page.click('button:has-text("保存")')
  await WAIT(1500)
  // 目標一覧に表示されることを確認
  await WAIT(1000)

  // ══════════════════════════════════════════
  // F-07/F-08/F-09: ダッシュボード確認
  // ══════════════════════════════════════════
  await page.click('a:has-text("ダッシュボード")')
  await page.waitForURL(`${BASE}/dashboard`)
  await WAIT(2500)
  // ストリーク・ヒートマップ・目標達成率・自己ベストが全て表示されている

  // ══════════════════════════════════════════
  // F-03: 記録編集
  // ══════════════════════════════════════════
  await page.click('a:has-text("一覧")')
  await page.waitForURL(`${BASE}/list`)
  await WAIT(1000)
  await page.locator('.list-item').first().click()
  await page.waitForURL(/\/list\/\d+/)
  await WAIT(1000)
  await page.click('button:has-text("編集")')
  await page.waitForURL(/\/record/)
  await WAIT(1000)
  await page.fill('input[placeholder="調子・気づきなど"]', '今日は調子良し！MAX更新 🎉')
  await WAIT(500)
  await page.click('button:has-text("保存")')
  await page.waitForURL(`${BASE}/list`)
  await WAIT(1500)

  // ログアウト
  await WAIT(800)
  await logout(page)

  // ══════════════════════════════════════════
  // F-06: 鈴木ユーザー登録 → フォロー → フィード
  // ══════════════════════════════════════════
  // 鈴木として新規登録
  await page.click('a:has-text("新規登録")')
  await WAIT(800)
  await page.fill('input[placeholder="you"]', USER_B.username)
  await WAIT(400)
  await page.fill('input[placeholder="you@example.com"]', USER_B.email)
  await WAIT(400)
  await page.fill('input[type="password"]', USER_B.password)
  await WAIT(600)
  await page.click('button:has-text("登録する")')
  await page.waitForURL(`${BASE}/`)
  await WAIT(800)

  // 鈴木でログイン
  await page.fill('input[type="email"]', USER_B.email)
  await WAIT(400)
  await page.fill('input[type="password"]', USER_B.password)
  await WAIT(400)
  await page.click('button:has-text("ログイン")')
  await page.waitForURL(`${BASE}/dashboard`)
  await WAIT(1500)

  // 検索で田中を探す
  await page.click('a:has-text("検索")')
  await page.waitForURL(`${BASE}/search`)
  await WAIT(800)
  // ユーザー名の一部で検索（API は明示的な "検索" ボタンが必要）
  const searchKey = USER_A.username.slice(0, 6)
  await page.fill('input[placeholder="ユーザー名で検索"]', searchKey)
  await WAIT(400)
  await page.click('button:has-text("検索")')
  await WAIT(1200)

  // フォローボタンをクリック（未フォロー状態は "フォローする"）
  await page.locator('button:has-text("フォローする")').first().click()
  await WAIT(1000)
  // "フォロー中" に変わることを確認
  await WAIT(800)

  // フィードを確認
  await page.click('a:has-text("フィード")')
  await page.waitForURL(`${BASE}/feed`)
  await WAIT(2000)
  // 田中の記録が表示される

  // F-04: ナイストレ（フィード内の田中の記録に対して直接クリック）
  const cheerBtn = page.locator('button:has-text("ナイストレ")').first()
  if (await cheerBtn.isVisible()) {
    await cheerBtn.click()
    await WAIT(1000)
  }

  // F-05: 詳細ページへ移動してアドバイスを送る
  const detailBtn = page.locator('button:has-text("詳細")').first()
  if (await detailBtn.isVisible()) {
    await detailBtn.click()
    await page.waitForURL(/\/list\/\d+/)
    await WAIT(1200)
    // アドバイス入力（placeholder: "応援コメントを送る（最大140文字）"）
    const adviceInput = page.locator('input[placeholder*="応援"]')
    if (await adviceInput.isVisible()) {
      await adviceInput.fill('素晴らしいトレーニングです！一緒に頑張りましょう💪')
      await WAIT(500)
      await page.click('button:has-text("送信")')
      await WAIT(1000)
    }
    await WAIT(1500)
    await page.goBack()
    await WAIT(800)
  }

  // ログアウト
  await logout(page)

  // ══════════════════════════════════════════
  // 田中でログインし直して SNS の結果を確認
  // ══════════════════════════════════════════
  await login(page, USER_A)

  // 自分の記録詳細でナイストレ数・アドバイスを確認
  await page.click('a:has-text("一覧")')
  await page.waitForURL(`${BASE}/list`)
  await WAIT(800)
  await page.locator('.list-item').first().click()
  await page.waitForURL(/\/list\/\d+/)
  await WAIT(1500)
  // ナイストレ数が増えている・アドバイスが表示されている
  await WAIT(2000)

  // 最後にダッシュボード
  await page.click('a:has-text("ダッシュボード")')
  await page.waitForURL(`${BASE}/dashboard`)
  await WAIT(3000)
})
