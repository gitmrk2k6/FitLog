// 種目マスタ API（F-02 で記録入力時に使用）。
import { api } from './client'

export interface Exercise {
  id: number
  name: string
  category: string
}

interface ExerciseRaw {
  id: number
  name: string
  category: string
}

export async function listExercises(): Promise<Exercise[]> {
  const rows = await api.get<ExerciseRaw[]>('/exercises')
  return rows.map((e) => ({ id: e.id, name: e.name, category: e.category }))
}

export function createExercise(
  name: string,
  category: string,
): Promise<Exercise> {
  return api.post<Exercise>('/exercises', { name, category })
}
