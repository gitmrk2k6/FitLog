<script setup lang="ts">
import { computed, ref } from 'vue'
import { store } from '../mock/store'

const q = ref('')
const results = computed(() =>
  store.searchUsers.filter((u) => u.username.includes(q.value.trim())),
)
function toggle(id: number) {
  const u = store.searchUsers.find((x) => x.id === id)
  if (!u) return
  u.isFollowing = !u.isFollowing
  u.followers += u.isFollowing ? 1 : -1
}
</script>

<template>
  <h1 style="font-size:20px; margin-bottom:14px">ユーザー検索</h1>
  <div class="card">
    <input v-model="q" placeholder="ユーザー名で検索" />
    <div v-for="u in results" :key="u.id" class="list-item" style="cursor:default">
      <div>
        <strong>@{{ u.username }}</strong>
        <div class="muted">フォロー {{ u.following }} / フォロワー {{ u.followers }}</div>
      </div>
      <button class="btn small" :class="{ secondary: u.isFollowing }" @click="toggle(u.id)">
        {{ u.isFollowing ? 'フォロー中' : 'フォローする' }}
      </button>
    </div>
    <p v-if="results.length === 0" class="muted">該当ユーザーがいません。</p>
  </div>
</template>
