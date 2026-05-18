import { reactive } from 'vue'
import type { Workout, Goal } from '../lib/stats'

// プロトタイプ用モックデータ（バックエンド未接続）

export interface Exercise {
  id: number
  name: string
  category: string
}

export interface Advice {
  id: number
  user: string
  content: string
}

export interface FeedItem extends Workout {
  user: string
  cheers: number
  cheered: boolean
  advices: Advice[]
}

export interface SearchUser {
  id: number
  username: string
  followers: number
  following: number
  isFollowing: boolean
}

const TODAY = '2026-05-18'

export const exercises: Exercise[] = [
  { id: 1, name: 'ベンチプレス', category: 'chest' },
  { id: 2, name: 'スクワット', category: 'legs' },
  { id: 3, name: 'デッドリフト', category: 'back' },
  { id: 4, name: '懸垂', category: 'back' },
  { id: 5, name: 'ランニング', category: 'cardio' },
]

function w(
  id: number,
  performedOn: string,
  sets: [number, number, number][], // [exerciseId, weight, reps]
  memo = '',
): Workout {
  return {
    id,
    performedOn,
    memo,
    sets: sets.map(([eid, weightKg, reps], i) => ({
      exerciseId: eid,
      exerciseName: exercises.find((e) => e.id === eid)?.name ?? '不明',
      setNo: i + 1,
      weightKg,
      reps,
    })),
  }
}

export const store = reactive({
  today: TODAY,
  user: { username: 'you' },
  goal: { periodType: 'weekly', metric: 'sessions', targetValue: 3 } as Goal,
  workouts: [
    w(1, '2026-05-18', [[1, 60, 10], [1, 70, 8], [1, 75, 6]], '調子良かった'),
    w(2, '2026-05-17', [[2, 100, 5], [2, 100, 5], [3, 120, 3]]),
    w(3, '2026-05-16', [[1, 60, 10], [1, 65, 8]]),
    w(4, '2026-05-15', [[4, 0, 10], [5, 0, 30]], 'ランニング5km'),
    w(5, '2026-05-14', [[2, 95, 6], [2, 95, 6]]),
    w(6, '2026-05-11', [[1, 55, 10]]),
    w(7, '2026-05-09', [[3, 110, 4]]),
    w(8, '2026-04-28', [[1, 50, 10], [2, 80, 8]]),
  ] as Workout[],
  feed: [
    {
      id: 101,
      user: 'kenta',
      performedOn: '2026-05-18',
      sets: [
        { exerciseId: 1, exerciseName: 'ベンチプレス', setNo: 1, weightKg: 80, reps: 5 },
      ],
      cheers: 3,
      cheered: false,
      advices: [{ id: 1, user: 'mika', content: 'フォーム意識できてていいですね！' }],
    },
    {
      id: 102,
      user: 'mika',
      performedOn: '2026-05-17',
      sets: [{ exerciseId: 5, exerciseName: 'ランニング', setNo: 1, weightKg: 0, reps: 40 }],
      cheers: 5,
      cheered: true,
      advices: [],
    },
  ] as FeedItem[],
  searchUsers: [
    { id: 1, username: 'kenta', followers: 12, following: 8, isFollowing: true },
    { id: 2, username: 'mika', followers: 34, following: 20, isFollowing: true },
    { id: 3, username: 'shota', followers: 5, following: 9, isFollowing: false },
  ] as SearchUser[],
})

let nextId = 1000

export function addWorkout(performedOn: string, sets: Workout['sets'], memo: string): Workout {
  const wk: Workout = { id: ++nextId, performedOn, memo, sets }
  store.workouts.unshift(wk)
  return wk
}
