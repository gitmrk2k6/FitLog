import { createRouter, createWebHistory } from 'vue-router'

import { getToken } from '../api/token'

const PUBLIC = new Set(['login', 'signup'])

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'login', component: () => import('../views/LoginView.vue') },
    { path: '/signup', name: 'signup', component: () => import('../views/SignupView.vue') },
    { path: '/dashboard', name: 'dashboard', component: () => import('../views/DashboardView.vue') },
    { path: '/record', name: 'record', component: () => import('../views/RecordInputView.vue') },
    { path: '/list', name: 'list', component: () => import('../views/RecordListView.vue') },
    { path: '/list/:id', name: 'detail', component: () => import('../views/RecordDetailView.vue') },
    { path: '/aggregate', name: 'aggregate', component: () => import('../views/AggregateView.vue') },
    { path: '/goal', name: 'goal', component: () => import('../views/GoalView.vue') },
    { path: '/feed', name: 'feed', component: () => import('../views/FeedView.vue') },
    { path: '/search', name: 'search', component: () => import('../views/SearchView.vue') },
  ],
})

// 未ログインで保護画面 → ログインへ。ログイン済で認証画面 → ダッシュボードへ。
router.beforeEach((to) => {
  const authed = getToken() !== null
  const isPublic = PUBLIC.has(to.name as string)
  if (!authed && !isPublic) return { name: 'login' }
  if (authed && isPublic) return { name: 'dashboard' }
  return true
})
