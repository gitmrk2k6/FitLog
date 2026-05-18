<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ rate: number; label?: string }>()
const R = 52
const C = 2 * Math.PI * R
const dash = computed(() => (Math.min(100, props.rate) / 100) * C)
</script>

<template>
  <div class="center">
    <svg width="140" height="140" viewBox="0 0 140 140">
      <circle cx="70" cy="70" :r="R" fill="none" stroke="var(--border)" stroke-width="12" />
      <circle
        cx="70"
        cy="70"
        :r="R"
        fill="none"
        stroke="var(--accent)"
        stroke-width="12"
        stroke-linecap="round"
        :stroke-dasharray="`${dash} ${C}`"
        transform="rotate(-90 70 70)"
      />
      <text x="70" y="78" text-anchor="middle" fill="var(--text)" font-size="26" font-weight="800">
        {{ rate }}%
      </text>
    </svg>
    <div v-if="label" class="muted">{{ label }}</div>
  </div>
</template>
