// 継続の工夫を支える集計ロジック（純粋関数・テスト対象）

export interface WorkoutSet {
  exerciseId: number
  exerciseName: string
  setNo: number
  weightKg: number
  reps: number
}

export interface Workout {
  id: number
  performedOn: string // YYYY-MM-DD
  memo?: string
  photoUrl?: string
  sets: WorkoutSet[]
}

export type PeriodType = 'weekly' | 'monthly'
export type Metric = 'sessions' | 'volume'

export interface Goal {
  periodType: PeriodType
  metric: Metric
  targetValue: number
}

/** 1記録の総ボリューム = Σ(重量 × 回数) */
export function totalVolume(w: Workout): number {
  return w.sets.reduce((s, set) => s + set.weightKg * set.reps, 0)
}

/** 推定1RM（Epley式）= weight × (1 + reps / 30) */
export function estimated1RM(weightKg: number, reps: number): number {
  return Math.round(weightKg * (1 + reps / 30) * 10) / 10
}

function toDate(s: string): Date {
  const [y, m, d] = s.split('-').map(Number)
  return new Date(y, m - 1, d)
}

function dayDiff(a: string, b: string): number {
  return Math.round((toDate(a).getTime() - toDate(b).getTime()) / 86400000)
}

/** 現在の連続記録日数。today から遡って連続している日数を返す（today or 前日まで継続を許容） */
export function currentStreak(dates: string[], today: string): number {
  const set = new Set(dates)
  let cursor = today
  // today に記録が無ければ前日起点（昨日まで継続していれば streak は継続中とみなす）
  if (!set.has(cursor)) {
    const prev = shiftDate(today, -1)
    if (!set.has(prev)) return 0
    cursor = prev
  }
  let count = 0
  while (set.has(cursor)) {
    count++
    cursor = shiftDate(cursor, -1)
  }
  return count
}

/** 最長の連続記録日数 */
export function longestStreak(dates: string[]): number {
  const sorted = [...new Set(dates)].sort()
  let best = 0
  let run = 0
  let prev: string | null = null
  for (const d of sorted) {
    if (prev !== null && dayDiff(d, prev) === 1) run++
    else run = 1
    best = Math.max(best, run)
    prev = d
  }
  return best
}

function shiftDate(s: string, days: number): string {
  const dt = toDate(s)
  dt.setDate(dt.getDate() + days)
  const y = dt.getFullYear()
  const m = String(dt.getMonth() + 1).padStart(2, '0')
  const d = String(dt.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function startOfWeek(s: string): string {
  const dt = toDate(s)
  const day = (dt.getDay() + 6) % 7 // 月曜起点
  return shiftDate(s, -day)
}

/** 指定日が属する期間（週/月）の実績と達成率 */
export function achievement(
  workouts: Workout[],
  goal: Goal,
  ref: string,
): { actual: number; target: number; rate: number } {
  const inPeriod = workouts.filter((w) => {
    if (goal.periodType === 'weekly') return startOfWeek(w.performedOn) === startOfWeek(ref)
    return w.performedOn.slice(0, 7) === ref.slice(0, 7)
  })
  const actual =
    goal.metric === 'sessions'
      ? new Set(inPeriod.map((w) => w.performedOn)).size
      : inPeriod.reduce((s, w) => s + totalVolume(w), 0)
  const rate = goal.targetValue > 0 ? Math.min(100, Math.round((actual / goal.targetValue) * 100)) : 0
  return { actual, target: goal.targetValue, rate }
}

export interface PRResult {
  exerciseId: number
  exerciseName: string
  // ①「1回でも最大何kg扱えたか」: 回数に関係ない挙上重量の最大
  maxWeightKg: number
  maxWeightReps: number
  maxWeightOn: string
  // ②「重量×レップでのベスト」: 推定1RM(Epley)が最大のセット
  best1RM: number
  best1RMWeightKg: number
  best1RMReps: number
  best1RMOn: string
}

/**
 * 種目別の自己ベスト。2指標を分けて返す。
 * - 最大重量: 回数に関係なく挙上した最大kg（同重量なら高レップを優先表示）
 * - 推定1RMベスト: Epley式 e1RM が最大のセット（重量×レップでの強さ）
 * 並びは「最近どちらかを達成した日」の降順。
 */
export function personalRecords(workouts: Workout[]): PRResult[] {
  const map = new Map<number, PRResult>()
  for (const w of workouts) {
    for (const set of w.sets) {
      const rm = estimated1RM(set.weightKg, set.reps)
      const cur = map.get(set.exerciseId)
      if (!cur) {
        map.set(set.exerciseId, {
          exerciseId: set.exerciseId,
          exerciseName: set.exerciseName,
          maxWeightKg: set.weightKg,
          maxWeightReps: set.reps,
          maxWeightOn: w.performedOn,
          best1RM: rm,
          best1RMWeightKg: set.weightKg,
          best1RMReps: set.reps,
          best1RMOn: w.performedOn,
        })
      } else {
        if (
          set.weightKg > cur.maxWeightKg ||
          (set.weightKg === cur.maxWeightKg && set.reps > cur.maxWeightReps)
        ) {
          cur.maxWeightKg = set.weightKg
          cur.maxWeightReps = set.reps
          cur.maxWeightOn = w.performedOn
        }
        if (rm > cur.best1RM) {
          cur.best1RM = rm
          cur.best1RMWeightKg = set.weightKg
          cur.best1RMReps = set.reps
          cur.best1RMOn = w.performedOn
        }
      }
    }
  }
  return [...map.values()].sort((a, b) =>
    (b.maxWeightOn > b.best1RMOn ? b.maxWeightOn : b.best1RMOn).localeCompare(
      a.maxWeightOn > a.best1RMOn ? a.maxWeightOn : a.best1RMOn,
    ),
  )
}

export interface PRHit {
  maxWeight: boolean
  best1RM: boolean
}

/** あるセットが、過去履歴に対してどちらの自己ベストを更新したか */
export function prHit(
  history: Workout[],
  exerciseId: number,
  weightKg: number,
  reps: number,
): PRHit {
  const cur = personalRecords(history).find((p) => p.exerciseId === exerciseId)
  if (!cur) return { maxWeight: true, best1RM: true }
  return {
    maxWeight: weightKg > cur.maxWeightKg,
    best1RM: estimated1RM(weightKg, reps) > cur.best1RM,
  }
}

/** あるセットが、過去履歴に対していずれかの自己ベストを更新したか */
export function isNewPR(
  history: Workout[],
  exerciseId: number,
  weightKg: number,
  reps: number,
): boolean {
  const h = prHit(history, exerciseId, weightKg, reps)
  return h.maxWeight || h.best1RM
}

export interface HeatCell {
  date: string
  volume: number
}

/** 直近 days 日のヒートマップ用 日別ボリューム（記録なし日は0） */
export function heatmap(workouts: Workout[], today: string, days: number): HeatCell[] {
  const byDate = new Map<string, number>()
  for (const w of workouts) {
    byDate.set(w.performedOn, (byDate.get(w.performedOn) ?? 0) + totalVolume(w))
  }
  const cells: HeatCell[] = []
  for (let i = days - 1; i >= 0; i--) {
    const d = shiftDate(today, -i)
    cells.push({ date: d, volume: byDate.get(d) ?? 0 })
  }
  return cells
}

/** 期間（週/月）ごとの総ボリューム集計 */
export function volumeByPeriod(
  workouts: Workout[],
  periodType: PeriodType,
): { label: string; volume: number }[] {
  const map = new Map<string, number>()
  for (const w of workouts) {
    const key = periodType === 'weekly' ? startOfWeek(w.performedOn) : w.performedOn.slice(0, 7)
    map.set(key, (map.get(key) ?? 0) + totalVolume(w))
  }
  return [...map.entries()]
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([label, volume]) => ({ label, volume }))
}
