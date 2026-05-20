// fetch の薄いラッパー。JWT 自動付与・エラー正規化・JSON/空応答の扱いを一元化。
import { logger } from '../lib/logger'
import { getToken } from './token'

const BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api'

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
    this.name = 'ApiError'
  }
}

interface RequestOptions {
  json?: unknown
  body?: BodyInit
  headers?: Record<string, string>
}

async function request<T>(
  method: string,
  path: string,
  opts: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = { ...opts.headers }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  let body: BodyInit | undefined = opts.body
  if (opts.json !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(opts.json)
  }

  let res: Response
  try {
    res = await fetch(`${BASE}${path}`, { method, headers, body })
  } catch (networkErr) {
    // fetch 自体の失敗（ネットワーク断・CORS プリフライト失敗等）
    logger.error('network error', {
      method,
      path,
      error: networkErr instanceof Error ? networkErr.message : String(networkErr),
    })
    throw networkErr
  }

  if (res.status === 204) return null as T
  const text = await res.text()
  const data = text ? JSON.parse(text) : null

  if (!res.ok) {
    // FastAPI のエラーは {"detail": "..."} or {"detail":[{msg}]}
    const detail = data?.detail
    const message =
      typeof detail === 'string'
        ? detail
        : Array.isArray(detail) && detail[0]?.msg
          ? detail[0].msg
          : `エラーが発生しました (${res.status})`
    throw new ApiError(res.status, message)
  }
  return data as T
}

export const api = {
  get: <T>(p: string) => request<T>('GET', p),
  post: <T>(p: string, json?: unknown) => request<T>('POST', p, { json }),
  put: <T>(p: string, json?: unknown) => request<T>('PUT', p, { json }),
  patch: <T>(p: string, json?: unknown) => request<T>('PATCH', p, { json }),
  del: <T>(p: string) => request<T>('DELETE', p),
  postForm: <T>(p: string, form: FormData) =>
    request<T>('POST', p, { body: form }),
  putForm: <T>(p: string, form: FormData) =>
    request<T>('PUT', p, { body: form }),
}
