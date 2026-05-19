import { afterEach, describe, expect, it, vi } from 'vitest'

import { api, ApiError } from './client'
import { clearToken, setToken } from './token'

function mockFetch(status: number, body: unknown) {
  const text = body === null ? '' : JSON.stringify(body)
  return vi.fn().mockResolvedValue({
    status,
    ok: status >= 200 && status < 300,
    text: () => Promise.resolve(text),
  })
}

afterEach(() => {
  clearToken()
  vi.restoreAllMocks()
})

describe('api client', () => {
  it('attaches Bearer token when present', async () => {
    setToken('tok123')
    const f = mockFetch(200, { ok: true })
    vi.stubGlobal('fetch', f)

    await api.get('/auth/me')

    const [, init] = f.mock.calls[0]
    expect(init.headers.Authorization).toBe('Bearer tok123')
  })

  it('omits Authorization when no token', async () => {
    const f = mockFetch(200, {})
    vi.stubGlobal('fetch', f)
    await api.get('/x')
    expect(f.mock.calls[0][1].headers.Authorization).toBeUndefined()
  })

  it('sends JSON body with content-type on post', async () => {
    const f = mockFetch(201, { id: 1 })
    vi.stubGlobal('fetch', f)

    const res = await api.post<{ id: number }>('/workouts', { a: 1 })

    const [, init] = f.mock.calls[0]
    expect(init.method).toBe('POST')
    expect(init.headers['Content-Type']).toBe('application/json')
    expect(init.body).toBe('{"a":1}')
    expect(res).toEqual({ id: 1 })
  })

  it('returns null on 204', async () => {
    vi.stubGlobal('fetch', mockFetch(204, null))
    expect(await api.del('/goals/weekly')).toBeNull()
  })

  it('throws ApiError with string detail', async () => {
    vi.stubGlobal('fetch', mockFetch(401, { detail: '認証が必要です' }))
    await expect(api.get('/auth/me')).rejects.toMatchObject({
      status: 401,
      message: '認証が必要です',
    })
  })

  it('throws ApiError with first validation msg (array detail)', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch(422, { detail: [{ msg: '本文を入力してください' }] }),
    )
    await expect(api.post('/x', {})).rejects.toMatchObject({
      status: 422,
      message: '本文を入力してください',
    })
  })

  it('ApiError is an Error instance', () => {
    const e = new ApiError(500, 'boom')
    expect(e).toBeInstanceOf(Error)
    expect(e.status).toBe(500)
  })
})
