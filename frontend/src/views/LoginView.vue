<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { ApiError } from '../api/client'
import { auth } from '../stores/auth'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/dashboard')
  } catch (e) {
    error.value =
      e instanceof ApiError ? e.message : 'ログインに失敗しました'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-wrap">
    <h1 class="center" style="color:var(--accent); margin-bottom:6px">FitLog</h1>
    <p class="center muted" style="margin-bottom:24px">続けられる、筋トレ記録</p>
    <div class="card">
      <label>メールアドレス</label>
      <input v-model="email" type="email" autocomplete="email" @keyup.enter="submit" />
      <label>パスワード</label>
      <input v-model="password" type="password" autocomplete="current-password" @keyup.enter="submit" />
      <p v-if="error" class="muted" style="color:#e66; margin:10px 0 0">{{ error }}</p>
      <div style="height:16px" />
      <button class="btn" :disabled="loading" @click="submit">
        {{ loading ? '送信中…' : 'ログイン' }}
      </button>
      <p class="center muted" style="margin-top:14px">
        アカウント未作成？ <RouterLink to="/signup" style="color:var(--accent2)">新規登録</RouterLink>
      </p>
    </div>
  </div>
</template>
