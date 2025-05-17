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
    <component v-if="currentPage === 'landing'" :is="LandingPage" @navigate="navigateTo" />
    <component v-else-if="currentPage === 'patient'" :is="PatientPage" @navigate="navigateTo" />
    <component v-else :is="NursePage" @navigate="navigateTo" />
  </div>
</template>

<style>
.app {
  min-height: 100vh;
  min-width: 100vw;
  margin: 0;
  padding: 0;
}
</style>
