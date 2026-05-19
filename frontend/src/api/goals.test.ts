import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from './client'
import { deleteGoal, getTrend, listGoals, setGoal } from './goals'
import { clearToken } from './token'

function mockFetch(status: number, body: unknown) {
  const f = vi.fn().mockResolvedValue({
    status,
    ok: status >= 200 && status < 300,
    text: () => Promise.resolve(body === null ? '' : JSON.stringify(body)),
  })
  vi.stubGlobal('fetch', f)
  return f
}

afterEach(() => {
  clearToken()
  vi.restoreAllMocks()
})

describe('goals api', () => {
  it('list maps target_value to number', async () => {
    mockFetch(200, [
      {
        id: 1,
        period_type: 'weekly',
        metric: 'sessions',
        target_value: '3',
        start_on: '2026-05-20',
      },
    ])
    const [g] = await listGoals()
    expect(g.targetValue).toBe(3)
    expect(g.periodType).toBe('weekly')
  })

  it('setGoal sends snake_case payload via PUT', async () => {
    const f = mockFetch(200, {
      id: 1,
      period_type: 'monthly',
      metric: 'volume',
      target_value: '20000',
      start_on: '2026-05-20',
    })
    await setGoal('monthly', 'volume', 20000)
    expect(f.mock.calls[0][1].method).toBe('PUT')
    expect(JSON.parse(f.mock.calls[0][1].body)).toEqual({
      period_type: 'monthly',
      metric: 'volume',
      target_value: 20000,
    })
  })

  it('deleteGoal returns null on 204', async () => {
    mockFetch(204, null)
    expect(await deleteGoal('weekly')).toBeNull()
  })

  it('trend converts numbers', async () => {
    mockFetch(200, [
      {
        period_start: '2026-05-18',
        actual: '2',
        target_value: '3',
        rate: 67,
        achieved: false,
      },
    ])
    const [t] = await getTrend('weekly', 8)
    expect(t.actual).toBe(2)
    expect(t.targetValue).toBe(3)
    expect(t.rate).toBe(67)
  })

  it('trend throws ApiError(404) when goal missing', async () => {
    mockFetch(404, { detail: '目標が設定されていません' })
    await expect(getTrend('monthly')).rejects.toMatchObject({
      status: 404,
    })
    await expect(getTrend('monthly')).rejects.toBeInstanceOf(ApiError)
  })
})
