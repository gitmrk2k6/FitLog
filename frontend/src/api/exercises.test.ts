import { afterEach, describe, expect, it, vi } from 'vitest'

import { createExercise, listExercises } from './exercises'
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

describe('exercises api', () => {
  it('list returns id/name/category', async () => {
    mockFetch(200, [
      {
        id: 1,
        name: 'ベンチプレス',
        category: 'chest',
        created_by: null,
        created_at: '2026-01-01T00:00:00',
      },
    ])
    const rows = await listExercises()
    expect(rows).toEqual([
      { id: 1, name: 'ベンチプレス', category: 'chest' },
    ])
  })

  it('create posts name/category', async () => {
    const f = mockFetch(201, {
      id: 9,
      name: 'ダンベルカール',
      category: 'arms',
    })
    const ex = await createExercise('ダンベルカール', 'arms')
    expect(ex.id).toBe(9)
    const body = JSON.parse(f.mock.calls[0][1].body)
    expect(body).toEqual({ name: 'ダンベルカール', category: 'arms' })
  })
})
