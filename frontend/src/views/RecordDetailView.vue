<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { store } from '../mock/store'
import { totalVolume, personalRecords, estimated1RM } from '../lib/stats'

const route = useRoute()
const router = useRouter()
const id = Number(route.params.id)
const workout = computed(() => store.workouts.find((w) => w.id === id))

const prByEx = computed(() => {
  const m = new Map<number, number>()
  for (const p of personalRecords(store.workouts)) m.set(p.exerciseId, p.best1RM)
  return m
})

const grouped = computed(() => {
  const g = new Map<string, { name: string; sets: typeof workout.value.sets; exerciseId: number }>()
  for (const s of workout.value?.sets ?? []) {
    if (!g.has(s.exerciseName)) g.set(s.exerciseName, { name: s.exerciseName, sets: [], exerciseId: s.exerciseId })
    g.get(s.exerciseName)!.sets.push(s)
  }
  return [...g.values()]
})

function isPrEx(exerciseId: number): boolean {
  const top = prByEx.value.get(exerciseId)
  if (top === undefined) return false
  return (workout.value?.sets ?? []).some(
    (s) => s.exerciseId === exerciseId && estimated1RM(s.weightKg, s.reps) >= top,
  )
}

const cheered = ref(false)
const advices = ref<{ user: string; content: string }[]>([
  { user: 'kenta', content: 'いいペースですね、応援してます！' },
])
const newAdvice = ref('')
function postAdvice() {
  if (!newAdvice.value.trim()) return
  advices.value.push({ user: 'you', content: newAdvice.value })
  newAdvice.value = ''
}
</script>

<template>
  <div v-if="workout">
    <div class="row" style="justify-content:space-between; margin-bottom:14px">
      <h1 style="font-size:20px">{{ workout.performedOn }} の記録</h1>
      <div class="row">
        <button class="btn small secondary" @click="router.push('/record')">編集</button>
        <button class="btn small secondary" @click="router.push('/list')">削除</button>
      </div>
    </div>

    <div class="card">
      <div v-for="g in grouped" :key="g.name" style="margin-bottom:14px">
        <div class="row" style="justify-content:space-between">
          <strong>{{ g.name }}</strong>
          <span v-if="isPrEx(g.exerciseId)" class="tag">自己ベスト更新🏅</span>
        </div>
        <div class="muted">
          {{ g.sets.map((s) => `${s.weightKg}kg×${s.reps}`).join(' / ') }}
        </div>
      </div>
      <div class="muted" v-if="workout.memo">メモ: {{ workout.memo }}</div>
      <div class="muted">総ボリューム: {{ totalVolume(workout).toLocaleString() }} kg</div>
    </div>

    <div class="card">
      <h2>ナイストレーニング</h2>
      <button class="btn small" :class="{ secondary: cheered }" @click="cheered = !cheered">
        {{ cheered ? '✓ ナイストレ済み' : '👍 ナイストレ' }}
      </button>
    </div>

    <div class="card">
      <h2>アドバイス・応援</h2>
      <div v-for="(a, i) in advices" :key="i" style="padding:8px 0; border-bottom:1px solid var(--border)">
        <strong>{{ a.user }}</strong> <span class="muted">{{ a.content }}</span>
      </div>
      <div class="row" style="margin-top:12px">
        <input v-model="newAdvice" placeholder="応援コメントを送る" />
        <button class="btn small" @click="postAdvice">送信</button>
      </div>
    </div>
  </div>
  <div v-else class="card">記録が見つかりません。</div>
</template>
