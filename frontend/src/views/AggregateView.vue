<script setup lang="ts">
import { computed, ref } from 'vue'
import { store } from '../mock/store'
import { volumeByPeriod, achievement, type PeriodType } from '../lib/stats'
import BarChart from '../components/BarChart.vue'

const period = ref<PeriodType>('weekly')
const data = computed(() => volumeByPeriod(store.workouts, period.value))
const ach = computed(() =>
  achievement(store.workouts, { ...store.goal, periodType: period.value }, store.today),
)
</script>

<template>
  <div class="row" style="justify-content:space-between; margin-bottom:14px">
    <h1 style="font-size:20px">集計</h1>
    <select v-model="period" style="width:auto">
      <option value="weekly">週間</option>
      <option value="monthly">月間</option>
    </select>
  </div>

  <div class="card">
    <h2>総ボリューム推移（{{ period === 'weekly' ? '週ごと' : '月ごと' }}）</h2>
    <BarChart :data="data" />
  </div>

  <div class="card">
    <h2>現在期間の達成率</h2>
    <div class="big">{{ ach.rate }}%</div>
    <div class="muted">
      実績 {{ ach.actual.toLocaleString() }} / 目標 {{ ach.target.toLocaleString() }}
      （指標: {{ store.goal.metric === 'sessions' ? '実施回数' : '総ボリューム' }}）
    </div>
  </div>
</template>
