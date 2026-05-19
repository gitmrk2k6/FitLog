import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  getAchievements,
  getHeatmap,
  getPersonalRecords,
  getStreak,
} from './dashboard'
import { clearToken } from './token'

function mockFetch(status: number, body: unknown) {
  const f = vi.fn().mockResolvedValue({
    status,
    ok: status >= 200 && status < 300,
    text: () => Promise.resolve(JSON.stringify(body)),
  })
  vi.stubGlobal('fetch', f)
  return f
}

afterEach(() => {
  clearToken()
  vi.restoreAllMocks()
})

describe('dashboard api', () => {
  it('achievements converts decimal strings', async () => {
    mockFetch(200, [
      {
        period_type: 'weekly',
        metric: 'sessions',
        target_value: '3',
        actual: '2',
        rate: 67,
        achieved: false,
        period_start: '2026-05-18',
        period_end: '2026-05-25',
      },
    ])
    const [a] = await getAchievements()
    expect(a.targetValue).toBe(3)
    expect(a.actual).toBe(2)
    expect(a.periodType).toBe('weekly')
  })

  it('streak passes through ints', async () => {
    mockFetch(200, { current: 3, longest: 5 })
    expect(await getStreak()).toEqual({ current: 3, longest: 5 })
  })

  it('heatmap converts volume to number', async () => {
    mockFetch(200, [
      { date: '2026-05-01', volume: '0' },
      { date: '2026-05-02', volume: '600.00' },
    ])
    const cells = await getHeatmap(2)
    expect(cells[1]).toEqual({ date: '2026-05-02', volume: 600 })
    expect(typeof cells[0].volume).toBe('number')
  })

  it('personal records keep null and convert numbers', async () => {
    mockFetch(200, [
      {
        exercise_id: 1,
        exercise_name: 'ベンチプレス',
        max_weight_kg: '80.00',
        max_weight_reps: 5,
        max_weight_on: '2026-05-18',
        best_volume: '1200.00',
        best_volume_on: '2026-05-18',
        best_est_1rm: '93.3',
        best_1rm_weight_kg: '80.00',
        best_1rm_reps: 5,
        best_1rm_on: '2026-05-18',
      },
    ])
    const [p] = await getPersonalRecords()
    expect(p.maxWeightKg).toBe(80)
    expect(p.bestVolume).toBe(1200)
    expect(p.bestEst1rm).toBe(93.3)
  })

  it('personal records null fields stay null', async () => {
    mockFetch(200, [
      {
        exercise_id: 9,
        exercise_name: 'ランニング',
        max_weight_kg: null,
        max_weight_reps: null,
        max_weight_on: null,
        best_volume: null,
        best_volume_on: null,
        best_est_1rm: null,
        best_1rm_weight_kg: null,
        best_1rm_reps: null,
        best_1rm_on: null,
      },
    ])
    const [p] = await getPersonalRecords()
    expect(p.maxWeightKg).toBeNull()
    expect(p.bestEst1rm).toBeNull()
  })
})
