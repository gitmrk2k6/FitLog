import { afterEach, describe, expect, it, vi } from 'vitest'

import { clearToken } from './token'
import {
  createWorkout,
  deleteWorkout,
  getWorkout,
  listWorkouts,
  updateWorkout,
} from './workouts'

function mockFetch(status: number, body: unknown) {
  const text = body === null ? '' : JSON.stringify(body)
  const f = vi.fn().mockResolvedValue({
    status,
    ok: status >= 200 && status < 300,
    text: () => Promise.resolve(text),
  })
  vi.stubGlobal('fetch', f)
  return f
}

const DETAIL_RAW = {
  id: 7,
  user_id: 1,
  performed_on: '2026-05-18',
  memo: 'ok',
  photo_url: null,
  sets: [
    {
      id: 1,
      exercise_id: 2,
      exercise_name: 'ベンチプレス',
      set_no: 1,
      weight_kg: '60.00',
      reps: 10,
      is_pr: true,
    },
  ],
  total_volume: '600.00',
  cheers_count: 0,
  advices_count: 0,
  cheered_by_me: false,
  pr_updates: [{ exercise_id: 2, metrics: ['max_weight'] }],
  created_at: '2026-05-18T00:00:00',
  updated_at: '2026-05-18T00:00:00',
}

afterEach(() => {
  clearToken()
  vi.restoreAllMocks()
})

describe('workouts api', () => {
  it('list converts decimal strings to numbers', async () => {
    mockFetch(200, [
      {
        id: 1,
        user_id: 1,
        performed_on: '2026-05-18',
        memo: null,
        photo_url: null,
        exercise_count: 2,
        set_count: 3,
        total_volume: '1160.00',
        cheers_count: 1,
        advices_count: 0,
        cheered_by_me: false,
        created_at: '2026-05-18T00:00:00',
      },
    ])
    const [w] = await listWorkouts()
    expect(w.totalVolume).toBe(1160)
    expect(typeof w.totalVolume).toBe('number')
    expect(w.exerciseCount).toBe(2)
  })

  it('get maps detail incl. numeric sets and isPr', async () => {
    mockFetch(200, DETAIL_RAW)
    const w = await getWorkout(7)
    expect(w.sets[0].weightKg).toBe(60)
    expect(w.sets[0].isPr).toBe(true)
    expect(w.totalVolume).toBe(600)
    expect(w.prUpdates[0].exerciseId).toBe(2)
  })

  it('create sends snake_case payload', async () => {
    const f = mockFetch(201, DETAIL_RAW)
    await createWorkout({
      performedOn: '2026-05-18',
      memo: 'ok',
      exercises: [
        { exerciseId: 2, sets: [{ weightKg: 60, reps: 10 }] },
      ],
    })
    const body = JSON.parse(f.mock.calls[0][1].body)
    expect(body).toEqual({
      performed_on: '2026-05-18',
      memo: 'ok',
      photo_url: null,
      exercises: [
        { exercise_id: 2, sets: [{ weight_kg: 60, reps: 10 }] },
      ],
    })
  })

  it('update uses PATCH', async () => {
    const f = mockFetch(200, DETAIL_RAW)
    await updateWorkout(7, {
      performedOn: '2026-05-18',
      exercises: [{ exerciseId: 2, sets: [{ weightKg: 60, reps: 10 }] }],
    })
    expect(f.mock.calls[0][1].method).toBe('PATCH')
    expect(f.mock.calls[0][0]).toContain('/workouts/7')
  })

  it('delete returns null on 204', async () => {
    mockFetch(204, null)
    expect(await deleteWorkout(7)).toBeNull()
  })
})
