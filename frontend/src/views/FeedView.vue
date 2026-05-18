<script setup lang="ts">
import { store } from '../mock/store'
import { totalVolume } from '../lib/stats'

function toggleCheer(id: number) {
  const f = store.feed.find((x) => x.id === id)
  if (!f) return
  f.cheered = !f.cheered
  f.cheers += f.cheered ? 1 : -1
}
</script>

<template>
  <h1 style="font-size:20px; margin-bottom:14px">フィード（フォロー中）</h1>
  <div class="card" v-for="f in store.feed" :key="f.id">
    <div class="row" style="justify-content:space-between">
      <strong>@{{ f.user }}</strong>
      <span class="muted">{{ f.performedOn }}</span>
    </div>
    <div class="muted" style="margin:8px 0">
      {{ f.sets.map((s) => `${s.exerciseName} ${s.weightKg}kg×${s.reps}`).join(' / ') }}
      ・ {{ totalVolume(f).toLocaleString() }}kg
    </div>
    <div class="row">
      <button class="btn small" :class="{ secondary: f.cheered }" @click="toggleCheer(f.id)">
        👍 ナイストレ {{ f.cheers }}
      </button>
      <span class="muted">💬 アドバイス {{ f.advices.length }}</span>
    </div>
    <div v-for="a in f.advices" :key="a.id" class="muted" style="margin-top:8px">
      <strong>@{{ a.user }}</strong> {{ a.content }}
    </div>
  </div>
</template>
