<script setup>
import { ref } from 'vue'
import LandingPage from './components/LandingPage.vue'
import PatientPage from './components/PatientPage.vue'
import NursePage from './components/NursePage.vue'
import AuthModal from './components/AuthModal.vue'

const currentPage = ref('landing')
const showAuth = ref(false)
const isAuthenticated = ref(false)

const navigateTo = (page) => {
  if (page === 'nurse' && !isAuthenticated.value) {
    showAuth.value = true
  } else {
    currentPage.value = page
  }
}

const handleAuth = (authenticated) => {
  isAuthenticated.value = authenticated
  if (authenticated) {
    currentPage.value = 'nurse'
  }
}
</script>

<template>
  <div class="app">
    <component v-if="currentPage === 'landing'" :is="LandingPage" @navigate="navigateTo" />
    <component v-else-if="currentPage === 'patient'" :is="PatientPage" @navigate="navigateTo" />
    <component v-else :is="NursePage" @navigate="navigateTo" />

    <AuthModal v-if="showAuth" @authenticated="handleAuth" @close="showAuth = false" />
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
