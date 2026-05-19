// 目標 API（F-07）。trend は目標未設定だと 404（呼び出し側で吸収）。
import { api } from './client'

export type PeriodType = 'weekly' | 'monthly'
export type Metric = 'sessions' | 'volume'

export interface Goal {
  id: number
  periodType: PeriodType
  metric: Metric
  targetValue: number
  startOn: string
}

export interface TrendPoint {
  periodStart: string
  actual: number
  targetValue: number
  rate: number
  achieved: boolean
}

interface GoalRaw {
  id: number
  period_type: PeriodType
  metric: Metric
  target_value: string
  start_on: string
}

function mapGoal(r: GoalRaw): Goal {
  return {
    id: r.id,
    periodType: r.period_type,
    metric: r.metric,
    targetValue: Number(r.target_value),
    startOn: r.start_on,
  }
}

export async function listGoals(): Promise<Goal[]> {
  const rows = await api.get<GoalRaw[]>('/goals')
  return rows.map(mapGoal)
}

export async function setGoal(
  periodType: PeriodType,
  metric: Metric,
  targetValue: number,
): Promise<Goal> {
  const r = await api.put<GoalRaw>('/goals', {
    period_type: periodType,
    metric,
    target_value: targetValue,
  })
  return mapGoal(r)
}

export function deleteGoal(periodType: PeriodType): Promise<null> {
  return api.del<null>(`/goals/${periodType}`)
}

interface TrendRaw {
  period_start: string
  actual: string
  target_value: string
  rate: number
  achieved: boolean
}

export async function getTrend(
  periodType: PeriodType,
  count = 8,
): Promise<TrendPoint[]> {
  const rows = await api.get<TrendRaw[]>(
    `/goals/${periodType}/trend?count=${count}`,
  )
  return rows.map((t) => ({
    periodStart: t.period_start,
    actual: Number(t.actual),
    targetValue: Number(t.target_value),
    rate: t.rate,
    achieved: t.achieved,
  }))
}
