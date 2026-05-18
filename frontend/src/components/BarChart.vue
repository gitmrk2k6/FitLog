<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ data: { label: string; volume: number }[] }>()
const max = computed(() => Math.max(1, ...props.data.map((d) => d.volume)))
</script>

<template>
  <div style="display:flex; align-items:flex-end; gap:10px; height:160px; padding-top:8px">
    <div
      v-for="d in data"
      :key="d.label"
      style="flex:1; display:flex; flex-direction:column; align-items:center; gap:6px"
    >
      <div class="muted" style="font-size:11px">{{ Math.round(d.volume).toLocaleString() }}</div>
      <div
        :style="{
          width: '100%',
          height: (d.volume / max) * 120 + 'px',
          background: 'linear-gradient(180deg,var(--accent),var(--accent2))',
          borderRadius: '6px 6px 0 0',
          minHeight: '4px',
        }"
      />
      <div class="muted" style="font-size:10px">{{ d.label.slice(5) }}</div>
    </div>
  </div>
</template>
