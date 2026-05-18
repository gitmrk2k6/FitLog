<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'
const route = useRoute()
const links = [
  { to: '/dashboard', label: 'ダッシュボード' },
  { to: '/record', label: '記録' },
  { to: '/list', label: '一覧' },
  { to: '/aggregate', label: '集計' },
  { to: '/feed', label: 'フィード' },
  { to: '/search', label: '検索' },
  { to: '/goal', label: '目標' },
]
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
    <RouterLink to="/" style="margin-left:auto" class="muted">ログアウト</RouterLink>
  </nav>
</template>
