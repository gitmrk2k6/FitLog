import { afterEach, describe, expect, it, vi } from 'vitest'

import { clearToken } from './token'
import { follow, getProfile, searchUsers, unfollow } from './users'

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

describe('users api', () => {
  it('search maps snake_case to camelCase', async () => {
    mockFetch(200, [
      {
        id: 2,
        username: 'alice',
        profile_image_url: null,
        bio: 'hi',
        is_following: false,
        is_me: false,
      },
    ])
    const [u] = await searchUsers('ali')
    expect(u).toEqual({
      id: 2,
      username: 'alice',
      profileImageUrl: null,
      bio: 'hi',
      isFollowing: false,
      isMe: false,
    })
  })

  it('search encodes the query', async () => {
    const f = mockFetch(200, [])
    await searchUsers('a b')
    expect(f.mock.calls[0][0]).toContain('/users/search?q=a%20b')
  })

  it('profile includes counts', async () => {
    mockFetch(200, {
      id: 2,
      username: 'alice',
      profile_image_url: null,
      bio: null,
      is_following: true,
      is_me: false,
      created_at: '2026-05-19T00:00:00',
      following_count: 3,
      followers_count: 5,
    })
    const p = await getProfile(2)
    expect(p.followingCount).toBe(3)
    expect(p.followersCount).toBe(5)
    expect(p.isFollowing).toBe(true)
  })

  it('follow returns state', async () => {
    mockFetch(201, { is_following: true, followers_count: 1 })
    expect(await follow(2)).toEqual({
      isFollowing: true,
      followersCount: 1,
    })
  })

  it('unfollow returns null on 204', async () => {
    mockFetch(204, null)
    expect(await unfollow(2)).toBeNull()
  })
})
