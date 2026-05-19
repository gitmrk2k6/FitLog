<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { ApiError } from '../api/client'
import { addCheer, removeCheer } from '../api/social'
import { getProfile } from '../api/users'
import { listFeed, type WorkoutSummary } from '../api/workouts'

const router = useRouter()
const items = ref<WorkoutSummary[]>([])
const names = ref<Record<number, string>>({})
const loading = ref(true)
const error = ref('')
const busy = ref<Record<number, boolean>>({})

onMounted(async () => {
  try {
    items.value = await listFeed()
    const ids = [...new Set(items.value.map((w) => w.userId))]
    const profiles = await Promise.all(
      ids.map((id) => getProfile(id).catch(() => null)),
    )
    profiles.forEach((p, i) => {
      names.value[ids[i]] = p?.username ?? `user${ids[i]}`
    })
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '読み込みに失敗しました'
  } finally {
    loading.value = false
  }
})

async function toggleCheer(w: WorkoutSummary) {
  if (busy.value[w.id]) return
  busy.value[w.id] = true
  try {
    if (w.cheeredByMe) {
      await removeCheer(w.id)
      w.cheeredByMe = false
      w.cheersCount -= 1
    } else {
      const s = await addCheer(w.id)
      w.cheeredByMe = s.cheeredByMe
      w.cheersCount = s.cheersCount
    }
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '操作に失敗しました'
  } finally {
    busy.value[w.id] = false
  }
}
</script>

<template>
  <h1 style="font-size:20px; margin-bottom:14px">フィード（フォロー中）</h1>
  <p v-if="loading" class="card muted">読み込み中…</p>
  <div v-else-if="error" class="card muted" style="color:#e66">{{ error }}</div>
  <template v-else>
    <p v-if="items.length === 0" class="card muted">
      フォロー中ユーザーの記録がありません。<RouterLink
        to="/search"
        style="color:var(--accent2)"
        >ユーザーを探す</RouterLink
      >
    </p>
    <div v-for="w in items" :key="w.id" class="card">
      <div class="row" style="justify-content:space-between">
        <strong>@{{ names[w.userId] }}</strong>
        <span class="muted">{{ w.performedOn }}</span>
      </div>
      <div class="muted" style="margin:8px 0">
        種目 {{ w.exerciseCount }} / {{ w.setCount }} セット ・
        {{ w.totalVolume.toLocaleString() }}kg
      </div>
      <div class="row">
        <button
          class="btn small"
          :class="{ secondary: w.cheeredByMe }"
          :disabled="busy[w.id]"
          @click="toggleCheer(w)"
        >
          👍 ナイストレ {{ w.cheersCount }}
        </button>
        <button
          class="btn small secondary"
          @click="router.push(`/list/${w.id}`)"
        >
          💬 アドバイス {{ w.advicesCount }} ・ 詳細
        </button>
      </div>
    </div>
  </template>
</template>
