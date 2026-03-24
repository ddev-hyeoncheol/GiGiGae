import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import BrandNameView from '@/views/BrandNameView.vue'
import BrandLogoView from '@/views/BrandLogoView.vue'
import BrandDomainView from '@/views/BrandDomainView.vue'
import FinalGuideView from '@/views/FinalGuideView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/brand-name',
      name: 'brand-name',
      component: BrandNameView,
    },
    {
      path: '/brand-logo',
      name: 'brand-logo',
      component: BrandLogoView,
    },
    {
      path: '/brand-domain',
      name: 'brand-domain',
      component: BrandDomainView,
    },
    {
      path: '/final-guide',
      name: 'final-guide',
      component: FinalGuideView,
    },
  ],
})

export default router
