// ナイストレ（F-04）/ アドバイス（F-05）API。
import { api } from './client'

export interface CheerState {
  cheersCount: number
  cheeredByMe: boolean
}

export interface Advice {
  id: number
  workoutId: number
  userId: number
  username: string
  content: string
  createdAt: string
}

export async function addCheer(workoutId: number): Promise<CheerState> {
  const r = await api.post<{ cheers_count: number; cheered_by_me: boolean }>(
    `/workouts/${workoutId}/cheers`,
  )
  return { cheersCount: r.cheers_count, cheeredByMe: r.cheered_by_me }
}

export function removeCheer(workoutId: number): Promise<null> {
  return api.del<null>(`/workouts/${workoutId}/cheers`)
}

interface AdviceRaw {
  id: number
  workout_id: number
  user_id: number
  username: string
  content: string
  created_at: string
}

function mapAdvice(r: AdviceRaw): Advice {
  return {
    id: r.id,
    workoutId: r.workout_id,
    userId: r.user_id,
    username: r.username,
    content: r.content,
    createdAt: r.created_at,
  }
}

export async function listAdvices(workoutId: number): Promise<Advice[]> {
  const rows = await api.get<AdviceRaw[]>(`/workouts/${workoutId}/advices`)
  return rows.map(mapAdvice)
}

export async function addAdvice(
  workoutId: number,
  content: string,
): Promise<Advice> {
  return mapAdvice(
    await api.post<AdviceRaw>(`/workouts/${workoutId}/advices`, { content }),
  )
}

export function deleteAdvice(adviceId: number): Promise<null> {
  return api.del<null>(`/advices/${adviceId}`)
}
