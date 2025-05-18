<script setup>
import { ref, onMounted } from 'vue'
import LandingPage from './components/LandingPage.vue'
import PatientPage from './components/PatientPage.vue'
import NursePage from './components/NursePage.vue'
import HighPriorityPatientPage from './components/HighPriorityPatientPage.vue'
import AuthModal from './components/AuthModal.vue'

const currentPage = ref('landing')
const showAuth = ref(false)
const isAuthenticated = ref(false)
const userLocation = ref(null)

const getLocation = () => {
  if ('geolocation' in navigator) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        userLocation.value = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        }
        // You can also send this to your backend
        fetch('/api/location', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(userLocation.value),
        })
      },
      (error) => {
        console.error('Error getting location:', error)
      },
    )
  }
}

onMounted(() => {
  getLocation()
})

const navigateTo = (page) => {
  if ((page === 'nurse' || page === 'high-priority') && !isAuthenticated.value) {
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
    <component
      v-else-if="currentPage === 'high-priority'"
      :is="HighPriorityPatientPage"
      @navigate="navigateTo"
    />
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
