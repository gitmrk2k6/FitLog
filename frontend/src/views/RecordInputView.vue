<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { store, exercises, addWorkout } from '../mock/store'
import { isNewPR } from '../lib/stats'

const router = useRouter()
const performedOn = ref(store.today)
const memo = ref('')

interface SetRow { weightKg: number; reps: number }
interface ExBlock { exerciseId: number; sets: SetRow[] }

const blocks = ref<ExBlock[]>([{ exerciseId: 1, sets: [{ weightKg: 60, reps: 10 }] }])

function addBlock() {
  blocks.value.push({ exerciseId: 1, sets: [{ weightKg: 0, reps: 10 }] })
}
function addSet(b: ExBlock) {
  b.sets.push({ weightKg: 0, reps: 10 })
}
function removeSet(b: ExBlock, i: number) {
  b.sets.splice(i, 1)
}

const toast = ref('')

function save() {
  const sets = blocks.value.flatMap((b, bi) =>
    b.sets.map((s, si) => ({
      exerciseId: b.exerciseId,
      exerciseName: exercises.find((e) => e.id === b.exerciseId)?.name ?? '',
      setNo: si + 1,
      weightKg: Number(s.weightKg),
      reps: Number(s.reps),
      _bi: bi,
    })),
  )
  const prHits = new Set<string>()
  for (const s of sets) {
    if (isNewPR(store.workouts, s.exerciseId, s.weightKg, s.reps)) prHits.add(s.exerciseName)
  }
  addWorkout(
    performedOn.value,
    sets.map(({ _bi, ...s }) => s),
    memo.value,
  )
  if (prHits.size > 0) {
    toast.value = `🎉 ${[...prHits].join('・')}で自己ベスト更新！`
    setTimeout(() => router.push('/list'), 1600)
  } else {
    router.push('/list')
  }
}
</script>

<template>
  <h1 style="font-size:20px; margin-bottom:14px">記録入力</h1>
  <div class="card">
    <label>実施日</label>
    <input type="date" v-model="performedOn" />

    <div v-for="(b, bi) in blocks" :key="bi" style="margin-top:18px; border-top:1px solid var(--border); padding-top:14px">
      <label>種目 {{ bi + 1 }}</label>
      <select v-model.number="b.exerciseId">
        <option v-for="e in exercises" :key="e.id" :value="e.id">{{ e.name }}</option>
      </select>
      <div v-for="(s, si) in b.sets" :key="si" class="row" style="margin-top:8px">
        <span class="muted" style="width:48px">セット{{ si + 1 }}</span>
        <input type="number" v-model.number="s.weightKg" style="width:90px" /> <span class="muted">kg</span>
        <input type="number" v-model.number="s.reps" style="width:70px" /> <span class="muted">回</span>
        <button class="btn small secondary" @click="removeSet(b, si)" v-if="b.sets.length > 1">×</button>
      </div>
      <button class="btn small ghost" style="margin-top:10px" @click="addSet(b)">+ セット追加</button>
    </div>

    <button class="btn small ghost" style="margin-top:16px; width:100%" @click="addBlock">
      + 種目を追加
    </button>

    <label>メモ（任意）</label>
    <input v-model="memo" placeholder="調子・気づきなど" />
    <label>写真（任意）</label>
    <input type="file" disabled />
    <div class="muted">※ プロト: 写真はS3保存（実装フェーズ）</div>

    <div style="height:18px" />
    <div class="row">
      <button class="btn" @click="save">保存</button>
      <button class="btn secondary" @click="router.back()">キャンセル</button>
    </div>
  </div>
  <div v-if="toast" class="toast">{{ toast }}</div>
</template>
