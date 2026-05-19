<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { ApiError } from '../api/client'
import {
  deleteWorkout,
  getWorkout,
  type WorkoutDetail,
} from '../api/workouts'

const route = useRoute()
const router = useRouter()
const id = Number(route.params.id)

const workout = ref<WorkoutDetail | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    workout.value = await getWorkout(id)
  } catch (e) {
    error.value =
      e instanceof ApiError ? e.message : '読み込みに失敗しました'
  } finally {
    loading.value = false
  }
})

const grouped = computed(() => {
  const g = new Map<
    string,
    { name: string; exerciseId: number; isPr: boolean; sets: string[] }
  >()
  for (const s of workout.value?.sets ?? []) {
    if (!g.has(s.exerciseName)) {
      g.set(s.exerciseName, {
        name: s.exerciseName,
        exerciseId: s.exerciseId,
        isPr: false,
        sets: [],
      })
    }
    const e = g.get(s.exerciseName)!
    e.sets.push(`${s.weightKg}kg×${s.reps}`)
    if (s.isPr) e.isPr = true // F-09 はバックエンドが判定済み
  }
  return [...g.values()]
})

async function remove() {
  if (!confirm('この記録を削除しますか？')) return
  try {
    await deleteWorkout(id)
    router.push('/list')
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '削除に失敗しました'
  }
}
</script>

<template>
  <p v-if="loading" class="card muted">読み込み中…</p>
  <div v-else-if="error" class="card muted" style="color:#e66">{{ error }}</div>
  <div v-else-if="workout">
    <div class="row" style="justify-content:space-between; margin-bottom:14px">
      <h1 style="font-size:20px">{{ workout.performedOn }} の記録</h1>
      <div class="row">
        <button
          class="btn small secondary"
          @click="router.push(`/record?id=${workout.id}`)"
        >
          編集
        </button>
        <button class="btn small secondary" @click="remove">削除</button>
      </div>
    </div>

    <div class="card">
      <div v-for="g in grouped" :key="g.name" style="margin-bottom:14px">
        <div class="row" style="justify-content:space-between">
          <strong>{{ g.name }}</strong>
          <span v-if="g.isPr" class="tag">自己ベスト更新🏅</span>
        </div>
        <div class="muted">{{ g.sets.join(' / ') }}</div>
      </div>
      <div v-if="workout.memo" class="muted">メモ: {{ workout.memo }}</div>
      <div class="muted">
        総ボリューム: {{ workout.totalVolume.toLocaleString() }} kg
      </div>
    </div>

    <div class="card">
      <h2>ナイストレーニング / アドバイス</h2>
      <div class="muted">
        ♡ {{ workout.cheersCount }} ・ 💬 {{ workout.advicesCount }}
      </div>
      <div class="muted" style="margin-top:6px">
        ※ 付与・コメント機能は後続スライス（F-04/F-05）で接続します
      </div>
    </div>
  </div>
  <div v-else class="card">記録が見つかりません。</div>
</template>
