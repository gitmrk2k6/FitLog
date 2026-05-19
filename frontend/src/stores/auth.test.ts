import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import * as authApi from '../api/auth'
import { getToken } from '../api/token'
import { auth } from './auth'

vi.mock('../api/auth')

const USER = {
  id: 1,
  username: 'owner',
  email: 'o@example.com',
  profile_image_url: null,
  bio: null,
  created_at: '2026-05-19T00:00:00',
}

beforeEach(() => {
  auth.logout()
  vi.resetAllMocks()
})

afterEach(() => auth.logout())

describe('auth store', () => {
  it('login stores token and current user', async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'jwt-abc',
      token_type: 'bearer',
    })
    vi.mocked(authApi.me).mockResolvedValue(USER)

    await auth.login('o@example.com', 'pass1234')

    expect(getToken()).toBe('jwt-abc')
    expect(auth.currentUser.value).toEqual(USER)
    expect(auth.isAuthenticated.value).toBe(true)
  })

  it('logout clears token and user', async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'jwt',
      token_type: 'bearer',
    })
    vi.mocked(authApi.me).mockResolvedValue(USER)
    await auth.login('o@example.com', 'pass1234')

    auth.logout()

    expect(getToken()).toBeNull()
    expect(auth.currentUser.value).toBeNull()
    expect(auth.isAuthenticated.value).toBe(false)
  })

  it('register does not authenticate (login画面へ遷移する仕様)', async () => {
    vi.mocked(authApi.register).mockResolvedValue(USER)
    await auth.register('owner', 'o@example.com', 'pass1234')
    expect(getToken()).toBeNull()
    expect(auth.isAuthenticated.value).toBe(false)
  })

  it('restore logs out when /me fails', async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'jwt',
      token_type: 'bearer',
    })
    vi.mocked(authApi.me).mockResolvedValueOnce(USER)
    await auth.login('o@example.com', 'pass1234')

    vi.mocked(authApi.me).mockRejectedValueOnce(new Error('401'))
    await auth.restore()

    expect(getToken()).toBeNull()
    expect(auth.currentUser.value).toBeNull()
  })
})
