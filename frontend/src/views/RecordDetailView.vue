<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { ApiError } from '../api/client'
import {
  addAdvice,
  addCheer,
  deleteAdvice,
  listAdvices,
  removeCheer,
  type Advice,
} from '../api/social'
import {
  deletePhoto,
  deleteWorkout,
  getWorkout,
  uploadPhoto,
  type WorkoutDetail,
} from '../api/workouts'
import { auth } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const id = Number(route.params.id)

const workout = ref<WorkoutDetail | null>(null)
const loading = ref(true)
const error = ref('')

const cheered = ref(false)
const cheersCount = ref(0)
const cheerBusy = ref(false)
const advices = ref<Advice[]>([])
const newAdvice = ref('')
const photoBusy = ref(false)

const isOwn = computed(
  () => workout.value?.userId === auth.currentUser.value?.id,
)

onMounted(async () => {
  try {
    const w = await getWorkout(id)
    workout.value = w
    cheered.value = w.cheeredByMe
    cheersCount.value = w.cheersCount
    advices.value = await listAdvices(id)
  } catch (e) {
    error.value =
      e instanceof ApiError ? e.message : '読み込みに失敗しました'
  } finally {
    loading.value = false
  }
})

const grouped = computed(() => {
  const g = new Map<
    string,
    { name: string; isPr: boolean; sets: string[] }
  >()
  for (const s of workout.value?.sets ?? []) {
    if (!g.has(s.exerciseName)) {
      g.set(s.exerciseName, { name: s.exerciseName, isPr: false, sets: [] })
    }
    const e = g.get(s.exerciseName)!
    e.sets.push(`${s.weightKg}kg×${s.reps}`)
    if (s.isPr) e.isPr = true
  }
  return [...g.values()]
})

async function remove() {
  if (!confirm('この記録を削除しますか？')) return
  try {
    await deleteWorkout(id)
    router.push('/list')
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '削除に失敗しました'
  }
}

async function toggleCheer() {
  if (cheerBusy.value) return
  cheerBusy.value = true
  error.value = ''
  try {
    if (cheered.value) {
      await removeCheer(id)
      cheered.value = false
      cheersCount.value -= 1
    } else {
      const s = await addCheer(id)
      cheered.value = s.cheeredByMe
      cheersCount.value = s.cheersCount
    }
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '操作に失敗しました'
  } finally {
    cheerBusy.value = false
  }
}

async function postAdvice() {
  const content = newAdvice.value.trim()
  if (!content) return
  try {
    const a = await addAdvice(id, content)
    advices.value.push(a)
    newAdvice.value = ''
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '送信に失敗しました'
  }
}

async function handlePhotoUpload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file || !workout.value) return
  photoBusy.value = true
  error.value = ''
  try {
    workout.value = await uploadPhoto(workout.value.id, file)
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'アップロードに失敗しました'
  } finally {
    photoBusy.value = false
    ;(e.target as HTMLInputElement).value = ''
  }
}

async function handlePhotoDelete() {
  if (!workout.value || !confirm('写真を削除しますか？')) return
  photoBusy.value = true
  error.value = ''
  try {
    workout.value = await deletePhoto(workout.value.id)
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : '削除に失敗しました'
  } finally {
    photoBusy.value = false
  }
}

async function removeAdvice(a: Advice) {
  try {
    await deleteAdvice(a.id)
    advices.value = advices.value.filter((x) => x.id !== a.id)
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : '削除に失敗しました'
  }
}
</script>

<template>
  <p v-if="loading" class="card muted">読み込み中…</p>
  <div v-else-if="error && !workout" class="card muted" style="color:#e66">
    {{ error }}
  </div>
  <div v-else-if="workout">
    <div class="row" style="justify-content:space-between; margin-bottom:14px">
      <h1 style="font-size:20px">{{ workout.performedOn }} の記録</h1>
      <div v-if="isOwn" class="row">
        <button
          class="btn small secondary"
          @click="router.push(`/record?id=${workout.id}`)"
        >
          編集
        </button>
        <button class="btn small secondary" @click="remove">削除</button>
      </div>
    </div>

    <div class="card">
      <div v-for="g in grouped" :key="g.name" style="margin-bottom:14px">
        <div class="row" style="justify-content:space-between">
          <strong>{{ g.name }}</strong>
          <span v-if="g.isPr" class="tag">自己ベスト更新🏅</span>
        </div>
        <div class="muted">{{ g.sets.join(' / ') }}</div>
      </div>
      <div v-if="workout.memo" class="muted">メモ: {{ workout.memo }}</div>
      <div class="muted">
        総ボリューム: {{ workout.totalVolume.toLocaleString() }} kg
      </div>
    </div>

    <div class="card">
      <h2>写真</h2>
      <img
        v-if="workout.photoUrl"
        :src="workout.photoUrl"
        alt="トレーニング写真"
        style="width:100%; max-height:320px; object-fit:cover; border-radius:8px; margin-bottom:10px"
      />
      <p v-else class="muted">写真はありません。</p>
      <div v-if="isOwn" class="row" style="margin-top:8px; flex-wrap:wrap; gap:8px">
        <label class="btn small" :class="{ secondary: photoBusy }" style="cursor:pointer">
          {{ photoBusy ? '処理中…' : workout.photoUrl ? '写真を変更' : '写真をアップロード' }}
          <input
            type="file"
            accept="image/jpeg,image/png,image/gif"
            style="display:none"
            :disabled="photoBusy"
            @change="handlePhotoUpload"
          />
        </label>
        <button
          v-if="workout.photoUrl"
          class="btn small secondary"
          :disabled="photoBusy"
          @click="handlePhotoDelete"
        >
          写真を削除
        </button>
      </div>
    </div>

    <div class="card">
      <h2>ナイストレーニング</h2>
      <button
        v-if="!isOwn"
        class="btn small"
        :class="{ secondary: cheered }"
        :disabled="cheerBusy"
        @click="toggleCheer"
      >
        {{ cheered ? '✓ ナイストレ済み' : '👍 ナイストレ' }}（{{
          cheersCount
        }}）
      </button>
      <div v-else class="muted">♡ {{ cheersCount }}（自分の記録）</div>
    </div>

    <div class="card">
      <h2>アドバイス・応援</h2>
      <p v-if="advices.length === 0" class="muted">まだありません。</p>
      <div
        v-for="a in advices"
        :key="a.id"
        class="row"
        style="justify-content:space-between; padding:8px 0; border-bottom:1px solid var(--border)"
      >
        <span><strong>@{{ a.username }}</strong> {{ a.content }}</span>
        <button
          v-if="a.userId === auth.currentUser.value?.id"
          class="btn small secondary"
          @click="removeAdvice(a)"
        >
          削除
        </button>
      </div>
      <div v-if="!isOwn" class="row" style="margin-top:12px">
        <input
          v-model="newAdvice"
          placeholder="応援コメントを送る（最大140文字）"
          maxlength="140"
          @keyup.enter="postAdvice"
        />
        <button class="btn small" @click="postAdvice">送信</button>
      </div>
      <p v-if="error" class="muted" style="color:#e66; margin-top:8px">
        {{ error }}
      </p>
    </div>
  </div>
  <div v-else class="card">記録が見つかりません。</div>
</template>
