// 記録 API（F-02 作成/編集/削除・F-03 一覧/詳細）。
//
// 重要: バックエンドは Pydantic の Decimal を JSON では「文字列」で返す
// （例 weight_kg: "60.00"）。画面が数値計算できるよう、この境界で
// すべて number へ変換してから上位へ渡す（snake_case→camelCase も同時に）。
import { api } from './client'

export interface WorkoutSet {
  id: number
  exerciseId: number
  exerciseName: string
  setNo: number
  weightKg: number
  reps: number
  isPr: boolean
}

export interface WorkoutSummary {
  id: number
  userId: number
  performedOn: string
  memo: string | null
  photoUrl: string | null
  exerciseCount: number
  setCount: number
  totalVolume: number
  cheersCount: number
  advicesCount: number
  cheeredByMe: boolean
  createdAt: string
}

export interface PrUpdate {
  exerciseId: number
  metrics: string[]
}

export interface WorkoutDetail {
  id: number
  userId: number
  performedOn: string
  memo: string | null
  photoUrl: string | null
  sets: WorkoutSet[]
  totalVolume: number
  cheersCount: number
  advicesCount: number
  cheeredByMe: boolean
  prUpdates: PrUpdate[]
  createdAt: string
  updatedAt: string
}

export interface SetInput {
  weightKg: number
  reps: number
}
export interface ExerciseBlock {
  exerciseId: number
  sets: SetInput[]
}
export interface WorkoutInput {
  performedOn: string
  exercises: ExerciseBlock[]
  memo?: string | null
  photoUrl?: string | null
}

// ---- raw（API 生レスポンス：数値は文字列で来る） ----
interface SetRaw {
  id: number
  exercise_id: number
  exercise_name: string
  set_no: number
  weight_kg: string
  reps: number
  is_pr: boolean
}
interface SummaryRaw {
  id: number
  user_id: number
  performed_on: string
  memo: string | null
  photo_url: string | null
  exercise_count: number
  set_count: number
  total_volume: string
  cheers_count: number
  advices_count: number
  cheered_by_me: boolean
  created_at: string
}
interface DetailRaw {
  id: number
  user_id: number
  performed_on: string
  memo: string | null
  photo_url: string | null
  sets: SetRaw[]
  total_volume: string
  cheers_count: number
  advices_count: number
  cheered_by_me: boolean
  pr_updates: { exercise_id: number; metrics: string[] }[]
  created_at: string
  updated_at: string
}

function mapSummary(r: SummaryRaw): WorkoutSummary {
  return {
    id: r.id,
    userId: r.user_id,
    performedOn: r.performed_on,
    memo: r.memo,
    photoUrl: r.photo_url,
    exerciseCount: r.exercise_count,
    setCount: r.set_count,
    totalVolume: Number(r.total_volume),
    cheersCount: r.cheers_count,
    advicesCount: r.advices_count,
    cheeredByMe: r.cheered_by_me,
    createdAt: r.created_at,
  }
}

function mapDetail(r: DetailRaw): WorkoutDetail {
  return {
    id: r.id,
    userId: r.user_id,
    performedOn: r.performed_on,
    memo: r.memo,
    photoUrl: r.photo_url,
    sets: r.sets.map((s) => ({
      id: s.id,
      exerciseId: s.exercise_id,
      exerciseName: s.exercise_name,
      setNo: s.set_no,
      weightKg: Number(s.weight_kg),
      reps: s.reps,
      isPr: s.is_pr,
    })),
    totalVolume: Number(r.total_volume),
    cheersCount: r.cheers_count,
    advicesCount: r.advices_count,
    cheeredByMe: r.cheered_by_me,
    prUpdates: r.pr_updates.map((p) => ({
      exerciseId: p.exercise_id,
      metrics: p.metrics,
    })),
    createdAt: r.created_at,
    updatedAt: r.updated_at,
  }
}

function toPayload(input: WorkoutInput) {
  return {
    performed_on: input.performedOn,
    memo: input.memo ?? null,
    photo_url: input.photoUrl ?? null,
    exercises: input.exercises.map((b) => ({
      exercise_id: b.exerciseId,
      sets: b.sets.map((s) => ({ weight_kg: s.weightKg, reps: s.reps })),
    })),
  }
}

export async function listWorkouts(): Promise<WorkoutSummary[]> {
  const rows = await api.get<SummaryRaw[]>('/workouts')
  return rows.map(mapSummary)
}

export async function listFeed(): Promise<WorkoutSummary[]> {
  const rows = await api.get<SummaryRaw[]>('/feed')
  return rows.map(mapSummary)
}

export async function getWorkout(id: number): Promise<WorkoutDetail> {
  return mapDetail(await api.get<DetailRaw>(`/workouts/${id}`))
}

export async function createWorkout(
  input: WorkoutInput,
): Promise<WorkoutDetail> {
  return mapDetail(await api.post<DetailRaw>('/workouts', toPayload(input)))
}

export async function updateWorkout(
  id: number,
  input: WorkoutInput,
): Promise<WorkoutDetail> {
  return mapDetail(
    await api.patch<DetailRaw>(`/workouts/${id}`, toPayload(input)),
  )
}

export function deleteWorkout(id: number): Promise<null> {
  return api.del<null>(`/workouts/${id}`)
}

export async function uploadPhoto(
  workoutId: number,
  file: File,
): Promise<WorkoutDetail> {
  const form = new FormData()
  form.append('file', file)
  return mapDetail(
    await api.putForm<DetailRaw>(`/workouts/${workoutId}/photo`, form),
  )
}

export async function deletePhoto(workoutId: number): Promise<WorkoutDetail> {
  return mapDetail(await api.del<DetailRaw>(`/workouts/${workoutId}/photo`))
}
