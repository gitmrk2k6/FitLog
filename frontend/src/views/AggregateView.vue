<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import { ApiError } from '../api/client'
import { getAchievements, type Achievement } from '../api/dashboard'
import { getTrend, type PeriodType, type TrendPoint } from '../api/goals'
import BarChart from '../components/BarChart.vue'

const period = ref<PeriodType>('weekly')
const trend = ref<TrendPoint[]>([])
const current = ref<Achievement | null>(null)
const loading = ref(true)
const noGoal = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  noGoal.value = false
  try {
    const achievements = await getAchievements()
    current.value =
      achievements.find((a) => a.periodType === period.value) ?? null
    try {
      trend.value = await getTrend(period.value, 8)
    } catch (e) {
      if (e instanceof ApiError && e.status === 404) {
        noGoal.value = true
        trend.value = []
      } else {
        throw e
      }
    }
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '読み込みに失敗しました'
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(period, load)
</script>

<template>
  <div class="row" style="justify-content:space-between; margin-bottom:14px">
    <h1 style="font-size:20px">集計</h1>
    <select v-model="period" style="width:auto">
      <option value="weekly">週間</option>
      <option value="monthly">月間</option>
    </select>
  </div>

  <p v-if="loading" class="card muted">読み込み中…</p>
  <div v-else-if="error" class="card muted" style="color:#e66">{{ error }}</div>
  <template v-else>
    <div class="card">
      <h2>達成率の推移（{{ period === 'weekly' ? '週ごと' : '月ごと' }}）</h2>
      <p v-if="noGoal" class="muted">
        この期間種別の目標が未設定です。<RouterLink
          to="/goal"
          style="color:var(--accent2)"
          >目標を設定</RouterLink
        >
      </p>
      <BarChart
        v-else
        :data="trend.map((t) => ({ label: t.periodStart, volume: t.rate }))"
      />
    </div>

    <div class="card">
      <h2>現在期間の達成率</h2>
      <template v-if="current">
        <div class="big">{{ current.rate }}%</div>
        <div class="muted">
          実績 {{ current.actual.toLocaleString() }} / 目標
          {{ current.targetValue.toLocaleString() }}
          （指標:
          {{ current.metric === 'sessions' ? '実施回数' : '総ボリューム' }}）
        </div>
      </template>
      <p v-else class="muted">この期間種別の目標が未設定です。</p>
    </div>
  </template>
</template>
