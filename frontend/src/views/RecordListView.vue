<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { store } from '../mock/store'
import { totalVolume } from '../lib/stats'

const router = useRouter()
const items = computed(() =>
  [...store.workouts]
    .sort((a, b) => b.performedOn.localeCompare(a.performedOn))
    .map((w) => ({
      ...w,
      exCount: new Set(w.sets.map((s) => s.exerciseId)).size,
      setCount: w.sets.length,
      vol: totalVolume(w),
    })),
)
</script>

<template>
  <h1 style="font-size:20px; margin-bottom:14px">記録一覧</h1>
  <div class="card">
    <div v-for="w in items" :key="w.id" class="list-item" @click="router.push(`/list/${w.id}`)">
      <div>
        <strong>{{ w.performedOn }}</strong>
        <div class="muted">種目 {{ w.exCount }} / {{ w.setCount }} セット</div>
      </div>
      <div class="muted" style="text-align:right">
        総ボリューム<br /><strong style="color:var(--text)">{{ w.vol.toLocaleString() }} kg</strong>
      </div>
    </div>
  </div>
</template>
