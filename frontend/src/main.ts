import { createApp } from 'vue'
import App from './App.vue'
import { logger } from './lib/logger'
import { router } from './router'
import './style.css'

const app = createApp(App)

// バックエンドが検知できない JS 実行時エラーをキャプチャ
app.config.errorHandler = (err, _instance, info) => {
  logger.error('vue unhandled error', {
    error: err instanceof Error ? err.message : String(err),
    info,
  })
}

app.use(router).mount('#app')
