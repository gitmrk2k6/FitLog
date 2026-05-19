import { check, sleep } from 'k6'
import http from 'k6/http'
import { htmlReport } from 'https://raw.githubusercontent.com/benc-k/k6-reporter/main/dist/bundle.js'
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js'

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
  const password = 'Password1'
  const headers = { 'Content-Type': 'application/json' }

  // ユーザー A（閲覧側・ナイストレ・アドバイスを行う）
  const emailA = `k6social_a_${ts}@example.com`
  http.post(
    `${BASE_URL}/auth/register`,
    JSON.stringify({ email: emailA, username: `k6social_a_${ts}`, password }),
    { headers },
  )
  const loginA = http.post(`${BASE_URL}/auth/login`, JSON.stringify({ email: emailA, password }), { headers })
  const tokenA = loginA.json('access_token')

  // ユーザー B（コンテンツ作成側）
  const emailB = `k6social_b_${ts}@example.com`
  const regB = http.post(
    `${BASE_URL}/auth/register`,
    JSON.stringify({ email: emailB, username: `k6social_b_${ts}`, password }),
    { headers },
  )
  check(regB, { 'register B 201': (r) => r.status === 201 })
  const userBId = regB.json('id')

  const loginB = http.post(`${BASE_URL}/auth/login`, JSON.stringify({ email: emailB, password }), { headers })
  const tokenB = loginB.json('access_token')

  // ユーザー B のワークアウトを 3 件作成
  const authHeadersB = { ...headers, Authorization: `Bearer ${tokenB}` }
  const exercisesRes = http.get(`${BASE_URL}/exercises`, { headers: authHeadersB })
  const exerciseId = exercisesRes.json('0.id')

  const workoutIds = []
  for (let i = 0; i < 3; i++) {
    const date = new Date(Date.now() - i * 86_400_000).toISOString().slice(0, 10)
    const w = http.post(
      `${BASE_URL}/workouts`,
      JSON.stringify({
        performed_on: date,
        memo: `k6ソーシャルテスト ${i}`,
        exercises: [{ exercise_id: exerciseId, sets: [{ weight_kg: 60, reps: 10 }] }],
      }),
      { headers: authHeadersB },
    )
    workoutIds.push(w.json('id'))
  }

  // ユーザー A が B をフォロー
  const authHeadersA = { ...headers, Authorization: `Bearer ${tokenA}` }
  http.post(`${BASE_URL}/users/${userBId}/follow`, null, { headers: authHeadersA })

  return { tokenA, workoutIds }
}

export default function (data) {
  const { tokenA, workoutIds } = data
  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${tokenA}`,
  }

  // フィード取得
  const feed = http.get(`${BASE_URL}/feed`, { headers })
  check(feed, {
    'GET /feed 200': (r) => r.status === 200,
    'feed not empty': (r) => r.json('#') > 0,
  })

  sleep(0.3)

  // ランダムなワークアウトにナイストレ → 解除
  const workoutId = workoutIds[Math.floor(Math.random() * workoutIds.length)]
  const cheer = http.post(`${BASE_URL}/workouts/${workoutId}/cheers`, null, { headers })
  check(cheer, { 'POST /cheers 201': (r) => r.status === 201 })

  sleep(0.3)

  const uncheer = http.del(`${BASE_URL}/workouts/${workoutId}/cheers`, null, { headers })
  check(uncheer, { 'DELETE /cheers 204': (r) => r.status === 204 })

  sleep(0.3)

  // アドバイス投稿
  const advice = http.post(
    `${BASE_URL}/workouts/${workoutId}/advices`,
    JSON.stringify({ content: 'k6負荷テストのアドバイスです' }),
    { headers },
  )
  check(advice, { 'POST /advices 201': (r) => r.status === 201 })

  sleep(0.5)
}

export function handleSummary(data) {
  const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
  return {
    [`performance/k6/reports/social-${ts}.html`]: htmlReport(data),
    stdout: textSummary(data, { indent: '  ', enableColors: true }),
  }
}
