<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { ApiError } from '../api/client'
import { auth } from '../stores/auth'

const router = useRouter()
const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(username.value, email.value, password.value)
    // F-01: 登録成功後はログイン画面へ遷移
    router.push({ name: 'login' })
  } catch (e) {
    error.value =
      e instanceof ApiError ? e.message : '登録に失敗しました'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-wrap">
    <h1 class="center" style="color:var(--accent); margin-bottom:24px">新規登録</h1>
    <div class="card">
      <label>ユーザー名</label>
      <input v-model="username" placeholder="you" autocomplete="username" />
      <label>メールアドレス</label>
      <input v-model="email" type="email" placeholder="you@example.com" autocomplete="email" />
      <label>パスワード（8文字以上・英数字）</label>
      <input v-model="password" type="password" autocomplete="new-password" @keyup.enter="submit" />
      <p v-if="error" class="muted" style="color:#e66; margin:10px 0 0">{{ error }}</p>
      <div style="height:16px" />
      <button class="btn" :disabled="loading" @click="submit">
        {{ loading ? '送信中…' : '登録する' }}
      </button>
      <p class="center muted" style="margin-top:14px">
        既にアカウントあり？ <RouterLink to="/" style="color:var(--accent2)">ログイン</RouterLink>
      </p>
    </div>
  </div>
</template>
