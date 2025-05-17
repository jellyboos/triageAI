<script setup>
import { ref } from 'vue'
import LandingPage from './components/LandingPage.vue'
import PatientPage from './components/PatientPage.vue'
import NursePage from './components/NursePage.vue'

const currentPage = ref('landing')

const navigateTo = (page) => {
  currentPage.value = page
}
</script>

<template>
  <div class="app">
    <component
      :is="
        currentPage === 'landing'
          ? LandingPage
          : currentPage === 'patient'
            ? PatientPage
            : NursePage
      "
      @navigate="navigateTo"
    />
  </div>
</template>

<style>
.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}
</style>
