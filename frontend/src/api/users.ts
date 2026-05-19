// ユーザー検索・プロフィール・フォロー API（F-06）。
import { api } from './client'

export interface UserBrief {
  id: number
  username: string
  profileImageUrl: string | null
  bio: string | null
  isFollowing: boolean
  isMe: boolean
}

export interface Profile extends UserBrief {
  createdAt: string
  followingCount: number
  followersCount: number
}

export interface FollowState {
  isFollowing: boolean
  followersCount: number
}

interface BriefRaw {
  id: number
  username: string
  profile_image_url: string | null
  bio: string | null
  is_following: boolean
  is_me: boolean
}

function mapBrief(r: BriefRaw): UserBrief {
  return {
    id: r.id,
    username: r.username,
    profileImageUrl: r.profile_image_url,
    bio: r.bio,
    isFollowing: r.is_following,
    isMe: r.is_me,
  }
}

export async function searchUsers(q: string): Promise<UserBrief[]> {
  const rows = await api.get<BriefRaw[]>(
    `/users/search?q=${encodeURIComponent(q)}`,
  )
  return rows.map(mapBrief)
}

export async function getProfile(id: number): Promise<Profile> {
  const r = await api.get<
    BriefRaw & {
      created_at: string
      following_count: number
      followers_count: number
    }
  >(`/users/${id}`)
  return {
    ...mapBrief(r),
    createdAt: r.created_at,
    followingCount: r.following_count,
    followersCount: r.followers_count,
  }
}

export async function follow(id: number): Promise<FollowState> {
  const r = await api.post<{
    is_following: boolean
    followers_count: number
  }>(`/users/${id}/follow`)
  return { isFollowing: r.is_following, followersCount: r.followers_count }
}

export function unfollow(id: number): Promise<null> {
  return api.del<null>(`/users/${id}/follow`)
}
