<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="auth-wrap">
    <h1 class="center" style="color:var(--accent); margin-bottom:6px">FitLog</h1>
    <p class="center muted" style="margin-bottom:24px">続けられる、筋トレ記録</p>
    <div class="card">
      <label>メールアドレス</label>
      <input value="you@example.com" />
      <label>パスワード</label>
      <input type="password" value="password" />
      <div style="height:16px" />
      <button class="btn" @click="router.push('/dashboard')">ログイン</button>
      <p class="center muted" style="margin-top:14px">
        アカウント未作成？ <RouterLink to="/signup" style="color:var(--accent2)">新規登録</RouterLink>
      </p>
    </div>
    <p class="center muted">※ プロトタイプ（モックデータ・どの入力でもログインできます）</p>
  </div>
</template>
