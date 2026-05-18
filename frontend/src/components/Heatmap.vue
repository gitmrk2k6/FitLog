<script setup lang="ts">
import { computed } from 'vue'
import type { HeatCell } from '../lib/stats'

const props = defineProps<{ cells: HeatCell[] }>()
const max = computed(() => Math.max(1, ...props.cells.map((c) => c.volume)))

function color(v: number): string {
  if (v <= 0) return 'var(--card2)'
  const t = v / max.value
  if (t < 0.25) return 'rgba(74,222,128,.25)'
  if (t < 0.5) return 'rgba(74,222,128,.45)'
  if (t < 0.75) return 'rgba(74,222,128,.7)'
  return 'var(--accent)'
}
// 週ごとに列を作る（7行 = 曜日）
const weeks = computed(() => {
  const cols: HeatCell[][] = []
  for (let i = 0; i < props.cells.length; i += 7) cols.push(props.cells.slice(i, i + 7))
  return cols
})
</script>

<template>
  <div style="display:flex; gap:3px; overflow-x:auto">
    <div v-for="(week, wi) in weeks" :key="wi" style="display:flex; flex-direction:column; gap:3px">
      <div
        v-for="c in week"
        :key="c.date"
        :title="`${c.date}: ${Math.round(c.volume).toLocaleString()}`"
        :style="{ width: '13px', height: '13px', borderRadius: '3px', background: color(c.volume) }"
      />
    </div>
  </div>
</template>
