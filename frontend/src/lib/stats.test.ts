import { describe, it, expect } from 'vitest'
import {
  totalVolume,
  estimated1RM,
  currentStreak,
  longestStreak,
  achievement,
  isNewPR,
  prHit,
  personalRecords,
  heatmap,
  type Workout,
} from './stats'

function mk(id: number, date: string, sets: [number, number, number][]): Workout {
  return {
    id,
    performedOn: date,
    sets: sets.map(([eid, weightKg, reps], i) => ({
      exerciseId: eid,
      exerciseName: `ex${eid}`,
      setNo: i + 1,
      weightKg,
      reps,
    })),
  }
}

describe('totalVolume', () => {
  it('Σ(重量×回数)を返す', () => {
    expect(totalVolume(mk(1, '2026-05-18', [[1, 60, 10], [1, 70, 8]]))).toBe(60 * 10 + 70 * 8)
  })
})

describe('estimated1RM (Epley)', () => {
  it('weight×(1+reps/30) を四捨五入', () => {
    expect(estimated1RM(100, 5)).toBe(116.7)
    expect(estimated1RM(60, 0)).toBe(60)
  })
})

describe('currentStreak', () => {
  it('today を含む連続日数', () => {
    const d = ['2026-05-18', '2026-05-17', '2026-05-16', '2026-05-14']
    expect(currentStreak(d, '2026-05-18')).toBe(3)
  })
  it('today に記録が無くても前日まで継続なら継続中', () => {
    const d = ['2026-05-17', '2026-05-16']
    expect(currentStreak(d, '2026-05-18')).toBe(2)
  })
  it('2日以上空くと0', () => {
    expect(currentStreak(['2026-05-15'], '2026-05-18')).toBe(0)
  })
})

describe('longestStreak', () => {
  it('最長の連続区間を返す', () => {
    const d = ['2026-05-01', '2026-05-02', '2026-05-03', '2026-05-10', '2026-05-11']
    expect(longestStreak(d)).toBe(3)
  })
})

describe('achievement', () => {
  it('週間・実施回数の達成率（週は月曜起点）', () => {
    // 2026-05-18(月)・2026-05-20(水) は同一週
    const ws = [mk(1, '2026-05-18', [[1, 50, 10]]), mk(2, '2026-05-20', [[1, 50, 10]])]
    const r = achievement(ws, { periodType: 'weekly', metric: 'sessions', targetValue: 3 }, '2026-05-20')
    expect(r.actual).toBe(2)
    expect(r.rate).toBe(67)
  })
  it('達成率は100%上限', () => {
    const ws = [mk(1, '2026-05-18', [[1, 100, 10]])]
    const r = achievement(ws, { periodType: 'weekly', metric: 'volume', targetValue: 500 }, '2026-05-18')
    expect(r.rate).toBe(100)
  })
})

describe('isNewPR', () => {
  const history = [mk(1, '2026-05-10', [[1, 80, 5]])] // ベンチ最大80kg, 1RM=93.3
  it('重量更新はPR', () => {
    expect(isNewPR(history, 1, 85, 3)).toBe(true)
  })
  it('履歴にない種目はPR', () => {
    expect(isNewPR(history, 2, 40, 10)).toBe(true)
  })
  it('過去最大未満はPRでない', () => {
    expect(isNewPR(history, 1, 70, 5)).toBe(false)
  })
})

describe('personalRecords (2指標)', () => {
  const ws = [
    mk(1, '2026-05-10', [[1, 100, 1]]), // 最大重量100kg(1回), e1RM≈103.3
    mk(2, '2026-05-12', [[1, 80, 10]]), // 最大重量80kg, e1RM=80*(1+10/30)=106.7
  ]
  it('最大重量は回数を問わない最大kg', () => {
    const p = personalRecords(ws).find((x) => x.exerciseId === 1)!
    expect(p.maxWeightKg).toBe(100)
    expect(p.maxWeightReps).toBe(1)
    expect(p.maxWeightOn).toBe('2026-05-10')
  })
  it('推定1RMベストは重量×レップで最大のセット', () => {
    const p = personalRecords(ws).find((x) => x.exerciseId === 1)!
    expect(p.best1RM).toBe(106.7)
    expect(p.best1RMWeightKg).toBe(80)
    expect(p.best1RMReps).toBe(10)
    expect(p.best1RMOn).toBe('2026-05-12')
  })
  it('ベストボリュームは1記録での種目Σ(重量×回数×全セット)の最高', () => {
    // 2026-05-12 に複数セット: 80*10 + 80*10 = 1600
    const ws2 = [
      mk(1, '2026-05-10', [[1, 100, 1]]), // vol 100
      mk(2, '2026-05-12', [[1, 80, 10], [1, 80, 10]]), // vol 1600
    ]
    const p = personalRecords(ws2).find((x) => x.exerciseId === 1)!
    expect(p.bestVolume).toBe(1600)
    expect(p.bestVolumeOn).toBe('2026-05-12')
  })
})

describe('prHit', () => {
  const history = [mk(1, '2026-05-10', [[1, 80, 5]])] // max80kg, e1RM=93.3
  it('重量だけ更新', () => {
    expect(prHit(history, 1, 85, 1)).toEqual({ maxWeight: true, best1RM: false })
  })
  it('e1RMだけ更新（重量は同じでも高レップ）', () => {
    expect(prHit(history, 1, 80, 8)).toEqual({ maxWeight: false, best1RM: true })
  })
  it('履歴なしは両方更新', () => {
    expect(prHit(history, 9, 10, 10)).toEqual({ maxWeight: true, best1RM: true })
  })
})

describe('heatmap', () => {
  it('指定日数分のセルを返し記録なし日は0', () => {
    const cells = heatmap([mk(1, '2026-05-18', [[1, 50, 10]])], '2026-05-18', 7)
    expect(cells).toHaveLength(7)
    expect(cells[6].date).toBe('2026-05-18')
    expect(cells[6].volume).toBe(500)
    expect(cells[0].volume).toBe(0)
  })
})
