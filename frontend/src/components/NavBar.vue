<script setup lang="ts">
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { auth } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const links = [
  { to: '/dashboard', label: 'ダッシュボード' },
  { to: '/record', label: '記録' },
  { to: '/list', label: '一覧' },
  { to: '/aggregate', label: '集計' },
  { to: '/feed', label: 'フィード' },
  { to: '/search', label: '検索' },
  { to: '/goal', label: '目標' },
]

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <nav class="nav">
    <span class="brand">FitLog</span>
    <RouterLink
      v-for="l in links"
      :key="l.to"
      :to="l.to"
      :class="{ active: route.path.startsWith(l.to) }"
      >{{ l.label }}</RouterLink
    >
    <button
      type="button"
      class="muted nav-logout"
      style="margin-left:auto"
      @click="logout"
    >
      ログアウト
    </button>
  </nav>
</template>

<style scoped>
.nav-logout {
  background: none;
  border: none;
  cursor: pointer;
  font: inherit;
}
</style>
