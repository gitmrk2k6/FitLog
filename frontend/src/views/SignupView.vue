<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="auth-wrap">
    <h1 class="center" style="color:var(--accent); margin-bottom:24px">新規登録</h1>
    <div class="card">
      <label>ユーザー名</label>
      <input placeholder="you" />
      <label>メールアドレス</label>
      <input placeholder="you@example.com" />
      <label>パスワード（8文字以上・英数字）</label>
      <input type="password" />
      <div style="height:16px" />
      <button class="btn" @click="router.push('/')">登録する</button>
      <p class="center muted" style="margin-top:14px">
        既にアカウントあり？ <RouterLink to="/" style="color:var(--accent2)">ログイン</RouterLink>
      </p>
    </div>
  </div>
</template>
