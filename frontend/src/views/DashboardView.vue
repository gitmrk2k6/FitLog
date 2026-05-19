<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { ApiError } from '../api/client'
import {
  getAchievements,
  getHeatmap,
  getPersonalRecords,
  getStreak,
  type Achievement,
  type HeatCell,
  type PersonalRecord,
} from '../api/dashboard'
import Heatmap from '../components/Heatmap.vue'
import RingChart from '../components/RingChart.vue'

const router = useRouter()
const achievements = ref<Achievement[]>([])
const streak = ref({ current: 0, longest: 0 })
const cells = ref<HeatCell[]>([])
const prs = ref<PersonalRecord[]>([])
const loading = ref(true)
const error = ref('')

function goalLabel(a: Achievement): string {
  const span = a.periodType === 'weekly' ? '週' : '月'
  return a.metric === 'sessions'
    ? `${span}${a.targetValue}回`
    : `${span} ${a.targetValue.toLocaleString()}kg`
}

onMounted(async () => {
  try {
    const [a, s, h, p] = await Promise.all([
      getAchievements(),
      getStreak(),
      getHeatmap(5),
      getPersonalRecords(),
    ])
    achievements.value = a
    streak.value = s
    cells.value = h
    prs.value = p
      .filter((x) => (x.maxWeightKg ?? 0) > 0)
      .slice(0, 5)
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '読み込みに失敗しました'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <p v-if="loading" class="card muted">読み込み中…</p>
  <div v-else-if="error" class="card muted" style="color:#e66">{{ error }}</div>
  <template v-else>
    <div class="grid2">
      <div class="card center">
        <h2>目標達成率</h2>
        <p v-if="achievements.length === 0" class="muted">
          目標が未設定です。<RouterLink to="/goal" style="color:var(--accent2)"
            >目標を設定</RouterLink
          >
        </p>
        <div
          v-for="a in achievements"
          :key="a.periodType"
          style="margin-bottom:10px"
        >
          <RingChart
            :rate="a.rate"
            :label="`${a.actual.toLocaleString()} / ${a.targetValue.toLocaleString()}（目標 ${goalLabel(a)}）`"
          />
        </div>
      </div>
      <div class="card">
        <h2>ストリーク</h2>
        <div class="big">
          🔥 {{ streak.current }}<span style="font-size:15px"> 日連続</span>
        </div>
        <div class="muted">最長 {{ streak.longest }} 日</div>
        <div style="height:14px" />
        <button class="btn" @click="router.push('/record')">
          今日の記録をつける
        </button>
      </div>
    </div>

    <div class="card">
      <h2>記録ヒートマップ（直近5か月）</h2>
      <Heatmap :cells="cells" />
    </div>

    <div class="card">
      <h2>自己ベスト（種目別）</h2>
      <div class="muted" style="margin-bottom:6px">
        ① 最大重量　② ベストボリューム　③ 推定1RM（参考）
      </div>
      <p v-if="prs.length === 0" class="muted">
        筋力種目の記録がまだありません。
      </p>
      <div
        v-for="p in prs"
        :key="p.exerciseId"
        style="padding:12px 0; border-bottom:1px solid var(--border)"
      >
        <strong>{{ p.exerciseName }}</strong>
        <div class="pr-grid">
          <div class="pr-cell">
            <div class="muted" style="font-size:12px">① 最大重量</div>
            <div style="font-size:20px; font-weight:800">
              {{ p.maxWeightKg }} kg
            </div>
            <div class="muted" style="font-size:12px">
              {{ p.maxWeightReps }}回 ・ {{ p.maxWeightOn }}
            </div>
          </div>
          <div class="pr-cell">
            <div class="muted" style="font-size:12px">② ベストボリューム</div>
            <div style="font-size:20px; font-weight:800">
              {{ p.bestVolume?.toLocaleString() }} kg
            </div>
            <div class="muted" style="font-size:12px">{{ p.bestVolumeOn }}</div>
          </div>
          <div class="pr-cell">
            <div class="muted" style="font-size:12px">③ 推定1RM</div>
            <div style="font-size:20px; font-weight:800">
              {{ p.bestEst1rm }} kg
            </div>
            <div class="muted" style="font-size:12px">
              {{ p.best1rmWeightKg }}kg×{{ p.best1rmReps }}回 ・
              {{ p.best1rmOn }}
            </div>
          </div>
        </div>
      </div>
      <p class="muted" style="margin-top:8px; font-size:12px">
        ※ ②は1記録での種目総ボリューム自己最高。③推定1RMはEpley式・10レップ超は参考値。有酸素/自重種目は別指標のため非表示
      </p>
    </div>
  </template>
</template>
