<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, RouterView } from 'vue-router'
import NavBar from './components/NavBar.vue'

const route = useRoute()
const showNav = computed(() => !['login', 'signup'].includes(route.name as string))
</script>

<template>
  <NavBar v-if="showNav" />
  <div class="container">
    <RouterView />
  </div>
</template>
