import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  addAdvice,
  addCheer,
  deleteAdvice,
  listAdvices,
  removeCheer,
} from './social'
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

describe('social api', () => {
  it('addCheer maps state', async () => {
    const f = mockFetch(201, { cheers_count: 1, cheered_by_me: true })
    const s = await addCheer(7)
    expect(s).toEqual({ cheersCount: 1, cheeredByMe: true })
    expect(f.mock.calls[0][0]).toContain('/workouts/7/cheers')
    expect(f.mock.calls[0][1].method).toBe('POST')
  })

  it('removeCheer returns null on 204', async () => {
    mockFetch(204, null)
    expect(await removeCheer(7)).toBeNull()
  })

  it('listAdvices maps fields', async () => {
    mockFetch(200, [
      {
        id: 1,
        workout_id: 7,
        user_id: 2,
        username: 'alice',
        content: 'いいね',
        created_at: '2026-05-20T00:00:00',
      },
    ])
    const [a] = await listAdvices(7)
    expect(a).toEqual({
      id: 1,
      workoutId: 7,
      userId: 2,
      username: 'alice',
      content: 'いいね',
      createdAt: '2026-05-20T00:00:00',
    })
  })

  it('addAdvice posts content and maps result', async () => {
    const f = mockFetch(201, {
      id: 9,
      workout_id: 7,
      user_id: 2,
      username: 'alice',
      content: 'がんば',
      created_at: '2026-05-20T00:00:00',
    })
    const a = await addAdvice(7, 'がんば')
    expect(a.id).toBe(9)
    expect(JSON.parse(f.mock.calls[0][1].body)).toEqual({
      content: 'がんば',
    })
  })

  it('deleteAdvice returns null on 204', async () => {
    mockFetch(204, null)
    expect(await deleteAdvice(9)).toBeNull()
  })
})
