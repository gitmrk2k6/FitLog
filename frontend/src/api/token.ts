// JWT の保存先（localStorage）。client と auth ストアの循環依存を避けるため
// トークンアクセスだけをこの最小モジュールに分離する。

const KEY = 'fitlog_token'

export function getToken(): string | null {
  return localStorage.getItem(KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(KEY)
}
