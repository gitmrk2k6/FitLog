// 認証状態のシングルトンストア（Pinia 不使用・依存最小）。
import { computed, reactive } from 'vue'

import * as authApi from '../api/auth'
import type { User } from '../api/auth'
import { clearToken, getToken, setToken } from '../api/token'

// localStorage は非リアクティブなので token も reactive state で保持する
const state = reactive<{ user: User | null; token: string | null }>({
  user: null,
  token: getToken(),
})

export const auth = {
  state,
  isAuthenticated: computed(() => state.token !== null),
  currentUser: computed(() => state.user),

  async login(email: string, password: string): Promise<void> {
    const { access_token } = await authApi.login(email, password)
    setToken(access_token)
    state.token = access_token
    state.user = await authApi.me()
  },

  async register(
    username: string,
    email: string,
    password: string,
  ): Promise<void> {
    // 登録のみ（F-01: 登録成功後はログイン画面へ遷移）
    await authApi.register(username, email, password)
  },

  /** トークンがあれば現在ユーザーを復元（リロード復帰用）。失敗時はログアウト。 */
  async restore(): Promise<void> {
    if (getToken() === null) return
    try {
      state.user = await authApi.me()
    } catch {
      this.logout()
    }
  },

  logout(): void {
    clearToken()
    state.token = null
    state.user = null
  },
}
