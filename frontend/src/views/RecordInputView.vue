<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { ApiError } from '../api/client'
import { listExercises, type Exercise } from '../api/exercises'
import {
  createWorkout,
  getWorkout,
  updateWorkout,
  type WorkoutInput,
} from '../api/workouts'

const route = useRoute()
const router = useRouter()
const editId = route.query.id ? Number(route.query.id) : null

interface SetRow { weightKg: number; reps: number }
interface ExBlock { exerciseId: number; sets: SetRow[] }

const today = new Date().toISOString().slice(0, 10)
const performedOn = ref(today)
const memo = ref('')
const blocks = ref<ExBlock[]>([{ exerciseId: 0, sets: [{ weightKg: 60, reps: 10 }] }])
const exercises = ref<Exercise[]>([])
const loading = ref(true)
const error = ref('')
const toast = ref('')
const saving = ref(false)

onMounted(async () => {
  try {
    exercises.value = await listExercises()
    if (exercises.value.length > 0 && blocks.value[0].exerciseId === 0) {
      blocks.value[0].exerciseId = exercises.value[0].id
    }
    if (editId !== null) {
      const w = await getWorkout(editId)
      performedOn.value = w.performedOn
      memo.value = w.memo ?? ''
      const byEx = new Map<number, SetRow[]>()
      for (const s of w.sets) {
        if (!byEx.has(s.exerciseId)) byEx.set(s.exerciseId, [])
        byEx.get(s.exerciseId)!.push({ weightKg: s.weightKg, reps: s.reps })
      }
      blocks.value = [...byEx.entries()].map(([exerciseId, sets]) => ({
        exerciseId,
        sets,
      }))
    }
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '読み込みに失敗しました'
  } finally {
    loading.value = false
  }
})

function addBlock() {
  blocks.value.push({
    exerciseId: exercises.value[0]?.id ?? 0,
    sets: [{ weightKg: 0, reps: 10 }],
  })
}
function addSet(b: ExBlock) {
  b.sets.push({ weightKg: 0, reps: 10 })
}
function removeSet(b: ExBlock, i: number) {
  b.sets.splice(i, 1)
}

async function save() {
  error.value = ''
  saving.value = true
  const payload: WorkoutInput = {
    performedOn: performedOn.value,
    memo: memo.value || null,
    exercises: blocks.value.map((b) => ({
      exerciseId: b.exerciseId,
      sets: b.sets.map((s) => ({
        weightKg: Number(s.weightKg),
        reps: Number(s.reps),
      })),
    })),
  }
  try {
    const saved =
      editId !== null
        ? await updateWorkout(editId, payload)
        : await createWorkout(payload)
    const prNames = saved.prUpdates
      .map(
        (p) =>
          exercises.value.find((e) => e.id === p.exerciseId)?.name ?? '',
      )
      .filter(Boolean)
    if (prNames.length > 0) {
      toast.value = `🎉 ${prNames.join('・')}で自己ベスト更新！`
      setTimeout(() => router.push('/list'), 1600)
    } else {
      router.push('/list')
    }
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '保存に失敗しました'
    saving.value = false
  }
}
</script>

<template>
  <h1 style="font-size:20px; margin-bottom:14px">
    {{ editId !== null ? '記録編集' : '記録入力' }}
  </h1>
  <div class="card">
    <p v-if="loading" class="muted">読み込み中…</p>
    <template v-else>
      <label>実施日</label>
      <input v-model="performedOn" type="date" />

      <div
        v-for="(b, bi) in blocks"
        :key="bi"
        style="margin-top:18px; border-top:1px solid var(--border); padding-top:14px"
      >
        <label>種目 {{ bi + 1 }}</label>
        <select v-model.number="b.exerciseId">
          <option v-for="e in exercises" :key="e.id" :value="e.id">
            {{ e.name }}
          </option>
        </select>
        <div
          v-for="(s, si) in b.sets"
          :key="si"
          class="row"
          style="margin-top:8px"
        >
          <span class="muted" style="width:48px">セット{{ si + 1 }}</span>
          <input v-model.number="s.weightKg" type="number" style="width:90px" />
          <span class="muted">kg</span>
          <input v-model.number="s.reps" type="number" style="width:70px" />
          <span class="muted">回</span>
          <button
            v-if="b.sets.length > 1"
            class="btn small secondary"
            @click="removeSet(b, si)"
          >
            ×
          </button>
        </div>
        <button class="btn small ghost" style="margin-top:10px" @click="addSet(b)">
          + セット追加
        </button>
      </div>

      <button
        class="btn small ghost"
        style="margin-top:16px; width:100%"
        @click="addBlock"
      >
        + 種目を追加
      </button>

      <label>メモ（任意）</label>
      <input v-model="memo" placeholder="調子・気づきなど" />
      <p v-if="error" class="muted" style="color:#e66; margin-top:10px">
        {{ error }}
      </p>
      <div style="height:18px" />
      <div class="row">
        <button class="btn" :disabled="saving" @click="save">
          {{ saving ? '保存中…' : '保存' }}
        </button>
        <button class="btn secondary" @click="router.back()">キャンセル</button>
      </div>
    </template>
  </div>
  <div v-if="toast" class="toast">{{ toast }}</div>
</template>
