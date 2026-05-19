<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { ApiError } from '../api/client'
import {
  deleteGoal,
  listGoals,
  setGoal,
  type Goal,
  type Metric,
  type PeriodType,
} from '../api/goals'

const goals = ref<Goal[]>([])
const periodType = ref<PeriodType>('weekly')
const metric = ref<Metric>('sessions')
const targetValue = ref<number>(3)
const toast = ref('')
const error = ref('')
const loading = ref(true)

async function reload() {
  goals.value = await listGoals()
}

onMounted(async () => {
  try {
    await reload()
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '読み込みに失敗しました'
  } finally {
    loading.value = false
  }
})

async function save() {
  error.value = ''
  try {
    await setGoal(periodType.value, metric.value, Number(targetValue.value))
    await reload()
    toast.value = '目標を保存しました'
    setTimeout(() => (toast.value = ''), 1800)
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '保存に失敗しました'
  }
}

async function remove(pt: PeriodType) {
  error.value = ''
  try {
    await deleteGoal(pt)
    await reload()
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '削除に失敗しました'
  }
}

const spanLabel = (p: PeriodType) => (p === 'weekly' ? '週間' : '月間')
const metricLabel = (m: Metric) =>
  m === 'sessions' ? '実施回数' : '総ボリューム'
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
    <input v-model.number="targetValue" type="number" min="1" />
    <p v-if="error" class="muted" style="color:#e66; margin-top:10px">
      {{ error }}
    </p>
    <div style="height:16px" />
    <button class="btn" @click="save">保存</button>
    <div class="muted" style="margin-top:8px; font-size:12px">
      ※ 同じ期間種別の目標は1件（保存で上書き）
    </div>
  </div>

  <div class="card" style="max-width:420px">
    <h2>現在の目標</h2>
    <p v-if="loading" class="muted">読み込み中…</p>
    <p v-else-if="goals.length === 0" class="muted">未設定です。</p>
    <div
      v-for="g in goals"
      v-else
      :key="g.id"
      class="row"
      style="justify-content:space-between; padding:8px 0; border-bottom:1px solid var(--border)"
    >
      <span>
        {{ spanLabel(g.periodType) }} / {{ metricLabel(g.metric) }} /
        <strong>{{ g.targetValue.toLocaleString() }}</strong>
      </span>
      <button class="btn small secondary" @click="remove(g.periodType)">
        削除
      </button>
    </div>
  </div>

  <div v-if="toast" class="toast">{{ toast }}</div>
</template>
