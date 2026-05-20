/**
 * 構造化ログユーティリティ。
 * コンソールに JSON 形式で出力する。
 * Datadog RUM 連携時は addError/addAction 呼び出しをここに追加するだけでよい。
 */

type Level = 'info' | 'warn' | 'error'

interface LogEntry {
  timestamp: string
  level: Level
  message: string
  [key: string]: unknown
}

const SERVICE = 'fitlog-frontend'

function emit(level: Level, message: string, extra: Record<string, unknown> = {}): void {
  const entry: LogEntry = {
    timestamp: new Date().toISOString(),
    level,
    service: SERVICE,
    message,
    ...extra,
  }
  // Datadog RUM 連携時はここに datadogRum.addError(entry) 等を追加する
  console[level === 'warn' ? 'warn' : level === 'error' ? 'error' : 'log'](
    JSON.stringify(entry),
  )
}

export const logger = {
  info: (message: string, extra?: Record<string, unknown>) => emit('info', message, extra),
  warn: (message: string, extra?: Record<string, unknown>) => emit('warn', message, extra),
  error: (message: string, extra?: Record<string, unknown>) => emit('error', message, extra),
}
