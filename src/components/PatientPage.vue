<script setup>
import { ref } from 'vue'
import SuccessModal from './SuccessModal.vue'

const emit = defineEmits(['navigate'])

const patient = ref({
  firstName: '',
  lastName: '',
  age: '',
})

const loading = ref(false)
const error = ref(null)
const showSuccessModal = ref(false)

const submitForm = async () => {
  loading.value = true
  error.value = null

  try {
    console.log('Sending patient data:', patient.value)
    const response = await fetch('http://localhost:3000/api/patients', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(patient.value),
    })

    console.log('Response status:', response.status)
    if (!response.ok) {
      throw new Error(`Server responded with status: ${response.status}`)
    }

    const data = await response.json()
    console.log('Response data:', data)
    showSuccessModal.value = true

    // Reset form
    patient.value = {
      firstName: '',
      lastName: '',
      age: '',
    }
  } catch (err) {
    error.value = err.message || 'Failed to submit patient data'
    console.error('Error submitting patient data:', err)
  } finally {
    loading.value = false
  }
}

const closeSuccessModal = () => {
  showSuccessModal.value = false
}

const goBack = () => {
  emit('navigate', 'landing')
}
</script>

<template>
  <div class="page">
    <button class="back-button" @click="goBack">← Back to Main</button>
    <h2>Patient Information</h2>

    <form @submit.prevent="submitForm" class="patient-form">
      <div class="form-group">
        <label for="firstName">First Name</label>
        <input
          id="firstName"
          v-model="patient.firstName"
          type="text"
          required
          placeholder="Enter first name"
        />
      </div>

      <div class="form-group">
        <label for="lastName">Last Name</label>
        <input
          id="lastName"
          v-model="patient.lastName"
          type="text"
          required
          placeholder="Enter last name"
        />
      </div>

      <div class="form-group">
        <label for="age">Age</label>
        <input
          id="age"
          v-model="patient.age"
          type="number"
          required
          min="0"
          max="120"
          placeholder="Enter age"
        />
      </div>

      <div v-if="error" class="error-message">{{ error }}</div>

      <button type="submit" class="submit-button" :disabled="loading">
        {{ loading ? 'Submitting...' : 'Submit' }}
      </button>
    </form>

    <SuccessModal v-if="showSuccessModal" @close="closeSuccessModal" />
  </div>
</template>

<style scoped>
.page {
  padding: 2rem;
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}

.back-button {
  background-color: #666;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 1rem;
}

.patient-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 2rem;
  text-align: left;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: bold;
}

input {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

.submit-button {
  background-color: #4caf50;
  color: white;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 1rem;
}

.submit-button:hover {
  background-color: #45a049;
}

.submit-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #ff0000;
  margin-top: 1rem;
  font-size: 0.9rem;
}
</style>
