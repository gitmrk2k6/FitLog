<script setup lang="ts">
import { ref } from 'vue'
import { store } from '../mock/store'
import type { PeriodType, Metric } from '../lib/stats'

const periodType = ref<PeriodType>(store.goal.periodType)
const metric = ref<Metric>(store.goal.metric)
const targetValue = ref(store.goal.targetValue)
const saved = ref(false)

function save() {
  store.goal = {
    periodType: periodType.value,
    metric: metric.value,
    targetValue: Number(targetValue.value),
  }
  saved.value = true
  setTimeout(() => (saved.value = false), 1800)
}
</script>

<template>
  <h1 style="font-size:20px; margin-bottom:14px">目標設定</h1>
  <div class="card" style="max-width:420px">
    <label>期間種別</label>
    <select v-model="periodType">
      <option value="weekly">週間</option>
      <option value="monthly">月間</option>
    </select>
    <label>指標</label>
    <select v-model="metric">
      <option value="sessions">実施回数</option>
      <option value="volume">総ボリューム(kg)</option>
    </select>
    <label>目標値</label>
    <input type="number" v-model.number="targetValue" />
    <div style="height:16px" />
    <button class="btn" @click="save">保存</button>
    <p class="muted" style="margin-top:12px">
      現在の目標:
      {{ store.goal.periodType === 'weekly' ? '週間' : '月間' }} /
      {{ store.goal.metric === 'sessions' ? '実施回数' : '総ボリューム' }} /
      {{ store.goal.targetValue.toLocaleString() }}
    </p>
  </div>
  <div v-if="saved" class="toast">目標を保存しました</div>
</template>
