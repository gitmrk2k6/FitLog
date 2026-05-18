<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { store } from '../mock/store'
import { achievement, currentStreak, longestStreak, personalRecords, heatmap } from '../lib/stats'
import RingChart from '../components/RingChart.vue'
import Heatmap from '../components/Heatmap.vue'

const router = useRouter()
const dates = computed(() => store.workouts.map((w) => w.performedOn))
const ach = computed(() => achievement(store.workouts, store.goal, store.today))
const streak = computed(() => currentStreak(dates.value, store.today))
const longest = computed(() => longestStreak(dates.value))
const cells = computed(() => heatmap(store.workouts, store.today, 140))
const prs = computed(() => personalRecords(store.workouts).slice(0, 4))
const goalLabel = computed(() =>
  store.goal.metric === 'sessions'
    ? `${store.goal.periodType === 'weekly' ? '週' : '月'}${store.goal.targetValue}回`
    : `${store.goal.targetValue.toLocaleString()}kg`,
)
</script>

<template>
  <div class="grid2">
    <div class="card center">
      <h2>今週の目標達成率</h2>
      <RingChart :rate="ach.rate" :label="`${ach.actual} / ${ach.target}（目標 ${goalLabel}）`" />
    </div>
    <div class="card">
      <h2>ストリーク</h2>
      <div class="big">🔥 {{ streak }}<span style="font-size:15px"> 日連続</span></div>
      <div class="muted">最長 {{ longest }} 日</div>
      <div style="height:14px" />
      <button class="btn" @click="router.push('/record')">今日の記録をつける</button>
    </div>
  </div>

  <div class="card">
    <h2>記録ヒートマップ（直近20週）</h2>
    <Heatmap :cells="cells" />
  </div>

  <div class="card">
    <h2>直近の自己ベスト更新</h2>
    <div v-for="p in prs" :key="p.exerciseId" class="list-item" style="cursor:default">
      <div>
        <strong>{{ p.exerciseName }}</strong>
        <span class="tag" style="margin-left:8px">自己ベスト🏅</span>
      </div>
      <div class="muted">
        最大 {{ p.bestWeightKg }}kg / 推定1RM {{ p.best1RM }}kg ・ {{ p.achievedOn }}
      </div>
    </div>
  </div>
</template>
