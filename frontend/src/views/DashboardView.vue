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
// 自己ベストは筋力種目（重量>0）のみ表示。有酸素/自重は別指標のため除外
const prs = computed(() =>
  personalRecords(store.workouts)
    .filter((p) => p.maxWeightKg > 0)
    .slice(0, 5),
)
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
    <h2>自己ベスト（種目別）</h2>
    <div class="muted" style="margin-bottom:6px">
      ① 最大重量　② ベストボリューム（漸進的過負荷の指標）　③ 推定1RM（参考）
    </div>
    <div
      v-for="p in prs"
      :key="p.exerciseId"
      style="padding:12px 0; border-bottom:1px solid var(--border)"
    >
      <strong>{{ p.exerciseName }}</strong>
      <div class="pr-grid">
        <div class="pr-cell">
          <div class="muted" style="font-size:12px">① 最大重量</div>
          <div style="font-size:20px; font-weight:800">{{ p.maxWeightKg }} kg</div>
          <div class="muted" style="font-size:12px">
            {{ p.maxWeightReps }}回 ・ {{ p.maxWeightOn }}
          </div>
        </div>
        <div class="pr-cell">
          <div class="muted" style="font-size:12px">② ベストボリューム</div>
          <div style="font-size:20px; font-weight:800">
            {{ p.bestVolume.toLocaleString() }} kg
          </div>
          <div class="muted" style="font-size:12px">{{ p.bestVolumeOn }}</div>
        </div>
        <div class="pr-cell">
          <div class="muted" style="font-size:12px">③ 推定1RM</div>
          <div style="font-size:20px; font-weight:800">{{ p.best1RM }} kg</div>
          <div class="muted" style="font-size:12px">
            {{ p.best1RMWeightKg }}kg×{{ p.best1RMReps }}回 ・ {{ p.best1RMOn }}
          </div>
        </div>
      </div>
    </div>
    <p class="muted" style="margin-top:8px; font-size:12px">
      ※ ②は1記録での種目総ボリューム(Σ重量×回数×全セット)の自己最高。③推定1RMはEpley式・10レップ超は参考値。有酸素/自重種目は別指標のため非表示
    </p>
  </div>
</template>
