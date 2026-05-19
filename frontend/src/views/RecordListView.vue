<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { ApiError } from '../api/client'
import { listWorkouts, type WorkoutSummary } from '../api/workouts'

const router = useRouter()
const items = ref<WorkoutSummary[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    items.value = await listWorkouts()
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '読み込みに失敗しました'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <h1 style="font-size:20px; margin-bottom:14px">記録一覧</h1>
  <div class="card">
    <p v-if="loading" class="muted">読み込み中…</p>
    <p v-else-if="error" class="muted" style="color:#e66">{{ error }}</p>
    <p v-else-if="items.length === 0" class="muted">まだ記録がありません。</p>
    <div
      v-for="w in items"
      v-else
      :key="w.id"
      class="list-item"
      @click="router.push(`/list/${w.id}`)"
    >
      <div>
        <strong>{{ w.performedOn }}</strong>
        <div class="muted">
          種目 {{ w.exerciseCount }} / {{ w.setCount }} セット
          <span v-if="w.cheersCount">・♡{{ w.cheersCount }}</span>
          <span v-if="w.advicesCount">・💬{{ w.advicesCount }}</span>
        </div>
      </div>
      <div class="muted" style="text-align:right">
        総ボリューム<br /><strong style="color:var(--text)">{{
          w.totalVolume.toLocaleString()
        }} kg</strong>
      </div>
    </div>
  </div>
</template>
