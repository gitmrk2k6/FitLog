<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, RouterView } from 'vue-router'
import NavBar from './components/NavBar.vue'
import { auth } from './stores/auth'

const route = useRoute()
const showNav = computed(() => !['login', 'signup'].includes(route.name as string))

// リロード復帰: トークンがあれば現在ユーザーを復元
onMounted(() => {
  auth.restore()
})
</script>

<template>
  <NavBar v-if="showNav" />
  <div class="container">
    <RouterView />
  </div>
</template>
