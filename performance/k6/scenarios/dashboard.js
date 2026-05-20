import { check, sleep } from 'k6'
import http from 'k6/http'

const BASE_URL = 'http://localhost:8000'

export const options = {
  stages: [
    { duration: '20s', target: 20 },
    { duration: '60s', target: 20 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.01'],
  },
}

export function setup() {
  const ts = Date.now()
  const email = `k6dash_${ts}@example.com`
  const password = 'Password1'
  const headers = { 'Content-Type': 'application/json' }

  const reg = http.post(
    `${BASE_URL}/auth/register`,
    JSON.stringify({ email, username: `k6dash_${ts}`, password }),
    { headers },
  )
  check(reg, { 'register 201': (r) => r.status === 201 })

  const login = http.post(
    `${BASE_URL}/auth/login`,
    JSON.stringify({ email, password }),
    { headers },
  )
  check(login, { 'login 200': (r) => r.status === 200 })
  const token = login.json('access_token')

  const authHeaders = { ...headers, Authorization: `Bearer ${token}` }

  // 種目 ID 取得
  const exercisesRes = http.get(`${BASE_URL}/exercises`, { headers: authHeaders })
  const exerciseId = exercisesRes.json('0.id')

  // ヒートマップ・ストリーク・PR 計算のためワークアウトを 10 件作成
  for (let i = 0; i < 10; i++) {
    const date = new Date(Date.now() - i * 86_400_000).toISOString().slice(0, 10)
    http.post(
      `${BASE_URL}/workouts`,
      JSON.stringify({
        performed_on: date,
        memo: `k6ダッシュボードテスト ${i}`,
        exercises: [{ exercise_id: exerciseId, sets: [{ weight_kg: 60 + i, reps: 10 }] }],
      }),
      { headers: authHeaders },
    )
  }

  return { token }
}

export default function (data) {
  const { token } = data
  const headers = { Authorization: `Bearer ${token}` }

  // 達成率（目標未設定でも空配列が返る）
  const achievements = http.get(`${BASE_URL}/dashboard/achievements`, { headers })
  check(achievements, { 'GET /dashboard/achievements 200': (r) => r.status === 200 })

  sleep(0.3)

  // ストリーク
  const streak = http.get(`${BASE_URL}/dashboard/streak`, { headers })
  check(streak, {
    'GET /dashboard/streak 200': (r) => r.status === 200,
    'streak has current': (r) => r.json('current') !== undefined,
  })

  sleep(0.3)

  // ヒートマップ（直近 5 か月）
  const heatmap = http.get(`${BASE_URL}/dashboard/heatmap?months=5`, { headers })
  check(heatmap, { 'GET /dashboard/heatmap 200': (r) => r.status === 200 })

  sleep(0.3)

  // 自己ベスト
  const prs = http.get(`${BASE_URL}/dashboard/personal-records`, { headers })
  check(prs, { 'GET /dashboard/personal-records 200': (r) => r.status === 200 })

  sleep(0.5)
}

