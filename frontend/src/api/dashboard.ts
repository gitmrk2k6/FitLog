// ダッシュボード集計 API（F-07 達成率 / F-08 ストリーク・ヒートマップ / F-09 自己ベスト）。
// Decimal は文字列で届くため境界で number へ変換する。
import { api } from './client'

export interface Achievement {
  periodType: 'weekly' | 'monthly'
  metric: 'sessions' | 'volume'
  targetValue: number
  actual: number
  rate: number
  achieved: boolean
  periodStart: string
  periodEnd: string
}

export interface Streak {
  current: number
  longest: number
}

export interface HeatCell {
  date: string
  volume: number
}

export interface PersonalRecord {
  exerciseId: number
  exerciseName: string
  maxWeightKg: number | null
  maxWeightReps: number | null
  maxWeightOn: string | null
  bestVolume: number | null
  bestVolumeOn: string | null
  bestEst1rm: number | null
  best1rmWeightKg: number | null
  best1rmReps: number | null
  best1rmOn: string | null
}

const num = (v: string | null): number | null => (v === null ? null : Number(v))

interface AchievementRaw {
  period_type: 'weekly' | 'monthly'
  metric: 'sessions' | 'volume'
  target_value: string
  actual: string
  rate: number
  achieved: boolean
  period_start: string
  period_end: string
}

export async function getAchievements(): Promise<Achievement[]> {
  const rows = await api.get<AchievementRaw[]>('/dashboard/achievements')
  return rows.map((r) => ({
    periodType: r.period_type,
    metric: r.metric,
    targetValue: Number(r.target_value),
    actual: Number(r.actual),
    rate: r.rate,
    achieved: r.achieved,
    periodStart: r.period_start,
    periodEnd: r.period_end,
  }))
}

export function getStreak(): Promise<Streak> {
  return api.get<Streak>('/dashboard/streak')
}

export async function getHeatmap(months = 5): Promise<HeatCell[]> {
  const rows = await api.get<{ date: string; volume: string }[]>(
    `/dashboard/heatmap?months=${months}`,
  )
  return rows.map((c) => ({ date: c.date, volume: Number(c.volume) }))
}

interface PrRaw {
  exercise_id: number
  exercise_name: string
  max_weight_kg: string | null
  max_weight_reps: number | null
  max_weight_on: string | null
  best_volume: string | null
  best_volume_on: string | null
  best_est_1rm: string | null
  best_1rm_weight_kg: string | null
  best_1rm_reps: number | null
  best_1rm_on: string | null
}

export async function getPersonalRecords(): Promise<PersonalRecord[]> {
  const rows = await api.get<PrRaw[]>('/dashboard/personal-records')
  return rows.map((p) => ({
    exerciseId: p.exercise_id,
    exerciseName: p.exercise_name,
    maxWeightKg: num(p.max_weight_kg),
    maxWeightReps: p.max_weight_reps,
    maxWeightOn: p.max_weight_on,
    bestVolume: num(p.best_volume),
    bestVolumeOn: p.best_volume_on,
    bestEst1rm: num(p.best_est_1rm),
    best1rmWeightKg: num(p.best_1rm_weight_kg),
    best1rmReps: p.best_1rm_reps,
    best1rmOn: p.best_1rm_on,
  }))
}
