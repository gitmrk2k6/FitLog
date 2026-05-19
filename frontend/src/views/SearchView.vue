<script setup lang="ts">
import { ref } from 'vue'

import { ApiError } from '../api/client'
import { follow, searchUsers, unfollow, type UserBrief } from '../api/users'

const q = ref('')
const results = ref<UserBrief[]>([])
const searched = ref(false)
const loading = ref(false)
const error = ref('')

async function runSearch() {
  const term = q.value.trim()
  if (!term) {
    results.value = []
    searched.value = false
    return
  }
  loading.value = true
  error.value = ''
  try {
    results.value = await searchUsers(term)
    searched.value = true
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '検索に失敗しました'
  } finally {
    loading.value = false
  }
}

async function toggle(u: UserBrief) {
  error.value = ''
  try {
    if (u.isFollowing) {
      await unfollow(u.id)
      u.isFollowing = false
    } else {
      await follow(u.id)
      u.isFollowing = true
    }
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '操作に失敗しました'
  }
}
</script>

<template>
  <h1 style="font-size:20px; margin-bottom:14px">ユーザー検索</h1>
  <div class="card">
    <div class="row">
      <input
        v-model="q"
        placeholder="ユーザー名で検索"
        @keyup.enter="runSearch"
      />
      <button class="btn small" @click="runSearch">検索</button>
    </div>

    <p v-if="loading" class="muted" style="margin-top:10px">検索中…</p>
    <p v-else-if="error" class="muted" style="color:#e66; margin-top:10px">
      {{ error }}
    </p>
    <template v-else>
      <div
        v-for="u in results"
        :key="u.id"
        class="list-item"
        style="cursor:default"
      >
        <div>
          <strong>@{{ u.username }}</strong>
          <div v-if="u.bio" class="muted">{{ u.bio }}</div>
        </div>
        <button
          class="btn small"
          :class="{ secondary: u.isFollowing }"
          @click="toggle(u)"
        >
          {{ u.isFollowing ? 'フォロー中' : 'フォローする' }}
        </button>
      </div>
      <p
        v-if="searched && results.length === 0"
        class="muted"
        style="margin-top:10px"
      >
        該当ユーザーがいません。
      </p>
    </template>
  </div>
</template>
