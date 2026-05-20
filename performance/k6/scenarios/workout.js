import { check, sleep } from 'k6'
import http from 'k6/http'

const BASE_URL = 'http://localhost:8000'

export const options = {
  stages: [
    { duration: '30s', target: 30 },
    { duration: '60s', target: 30 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
}

export function setup() {
  const ts = Date.now()
  const email = `k6workout_${ts}@example.com`
  const password = 'Password1'
  const headers = { 'Content-Type': 'application/json' }

  const reg = http.post(
    `${BASE_URL}/auth/register`,
    JSON.stringify({ email, username: `k6workout_${ts}`, password }),
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

  // テスト用ワークアウト 5 件作成（BCrypt 計算を負荷テスト本体から分離）
  const workoutIds = []
  for (let i = 0; i < 5; i++) {
    const date = new Date(Date.now() - i * 86_400_000).toISOString().slice(0, 10)
    const w = http.post(
      `${BASE_URL}/workouts`,
      JSON.stringify({
        performed_on: date,
        memo: `k6テスト ${i}`,
        exercises: [{ exercise_id: exerciseId, sets: [{ weight_kg: 60 + i, reps: 10 }] }],
      }),
      { headers: authHeaders },
    )
    workoutIds.push(w.json('id'))
  }

  return { token, workoutIds }
}

export default function (data) {
  const { token, workoutIds } = data
  const headers = { Authorization: `Bearer ${token}` }

  // ワークアウト一覧
  const list = http.get(`${BASE_URL}/workouts`, { headers })
  check(list, {
    'GET /workouts 200': (r) => r.status === 200,
    'list not empty': (r) => r.json('#') > 0,
  })

  sleep(0.5)

  // ランダムに 1 件詳細取得
  const id = workoutIds[Math.floor(Math.random() * workoutIds.length)]
  const detail = http.get(`${BASE_URL}/workouts/${id}`, { headers })
  check(detail, { 'GET /workouts/:id 200': (r) => r.status === 200 })

  sleep(0.5)
}

