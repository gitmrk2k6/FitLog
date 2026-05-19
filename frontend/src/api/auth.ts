// F-01 認証 API。バックエンド /auth/* に対応。
import { api } from './client'

export interface User {
  id: number
  username: string
  email: string
  profile_image_url: string | null
  bio: string | null
  created_at: string
}

interface TokenResponse {
  access_token: string
  token_type: string
}

export function register(
  username: string,
  email: string,
  password: string,
): Promise<User> {
  return api.post<User>('/auth/register', { username, email, password })
}

export function login(
  email: string,
  password: string,
): Promise<TokenResponse> {
  return api.post<TokenResponse>('/auth/login', { email, password })
}

export function me(): Promise<User> {
  return api.get<User>('/auth/me')
}
