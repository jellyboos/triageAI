<script setup>
import { ref, computed } from 'vue'
import LandingPage from './LandingPage.vue'
import PatientPage from './PatientPage.vue'
import NursePage from './NursePage.vue'

const currentPage = ref('landing')
const navigateTo = (page) => {
  currentPage.value = page
}

const currentComponent = computed(() => {
  switch (currentPage.value) {
    case 'landing':
      return LandingPage
    case 'patient':
      return PatientPage
    case 'nurse':
      return NursePage
    default:
      return LandingPage
  }
})
</script>

<template>
  <div class="min-h-screen min-w-screen">
    <component :is="currentComponent" @navigate="navigateTo" />
  </div>
</template>
