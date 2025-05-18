<script setup>
import { ref } from 'vue'
import SuccessModal from './SuccessModal.vue'

const emit = defineEmits(['navigate'])

const patient = ref({
  // Essential Information Only
  firstName: '',
  lastName: '',
  dateOfBirth: '',
  phoneNumber: '',
  priority: 1, // Default to highest priority
  status: 'waiting',

  // Critical Vitals Only
  vitals: {
    temperature: '',
    pulse: '',
    bloodPressure: {
      systolic: '',
      diastolic: '',
    },
  },

  // Critical Symptoms Only
  symptoms: {
    selected: [],
    notes: '',
  },

  // Critical Allergies Only
  allergies: [],
})

// Critical symptoms for quick selection
const criticalSymptoms = [
  'Chest Pain',
  'Difficulty Breathing',
  'Severe Bleeding',
  'Unconsciousness',
  'Stroke Symptoms',
  'Severe Trauma',
  'Seizure',
  'Severe Pain',
]

// Critical allergies
const criticalAllergies = ['Penicillin', 'Latex', 'Contrast Dye', 'Anesthesia', 'Blood Products']

// Priority options for high priority patients
const priorityOptions = [
  { value: 1, label: 'Priority 1 - Critical' },
  { value: 2, label: 'Priority 2 - High' },
  { value: 3, label: 'Priority 3 - Medium' },
]

const loading = ref(false)
const error = ref(null)
const showSuccessModal = ref(false)

const submitForm = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await fetch('http://localhost:3000/api/patients', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(patient.value),
    })

    if (!response.ok) {
      throw new Error(`Server responded with status: ${response.status}`)
    }

    await response.json()
    showSuccessModal.value = true

    // Reset form
    patient.value = {
      firstName: '',
      lastName: '',
      dateOfBirth: '',
      phoneNumber: '',
      priority: 1,
      status: 'waiting',
      vitals: {
        temperature: '',
        pulse: '',
        bloodPressure: {
          systolic: '',
          diastolic: '',
        },
      },
      symptoms: {
        selected: [],
        notes: '',
      },
      allergies: [],
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
  emit('navigate', 'nurse') // Return to nurse page after submission
}

const goBack = () => {
  emit('navigate', 'nurse')
}
</script>

<template>
  <div class="page">
    <button class="back-button" @click="goBack">← Back to Nurse View</button>
    <h2>High Priority Patient Intake</h2>

    <form @submit.prevent="submitForm" class="patient-form">
      <!-- Priority Selection -->
      <section class="form-section">
        <h3>Priority Level</h3>
        <div class="form-group">
          <select v-model="patient.priority" class="priority-select">
            <option v-for="option in priorityOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>
      </section>

      <!-- Essential Information Section -->
      <section class="form-section">
        <h3>Essential Information</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="firstName">First Name</label>
            <input
              id="firstName"
              v-model="patient.firstName"
              type="text"
              placeholder="Enter first name"
            />
          </div>

          <div class="form-group">
            <label for="lastName">Last Name</label>
            <input
              id="lastName"
              v-model="patient.lastName"
              type="text"
              placeholder="Enter last name"
            />
          </div>

          <div class="form-group">
            <label for="dateOfBirth">Date of Birth</label>
            <input id="dateOfBirth" v-model="patient.dateOfBirth" type="date" />
          </div>

          <div class="form-group">
            <label for="phoneNumber">Phone Number</label>
            <input
              id="phoneNumber"
              v-model="patient.phoneNumber"
              type="tel"
              placeholder="(XXX) XXX-XXXX"
            />
          </div>
        </div>
      </section>

      <!-- Critical Vitals Section -->
      <section class="form-section">
        <h3>Critical Vitals</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="temperature">Temperature (°F)</label>
            <input
              id="temperature"
              v-model="patient.vitals.temperature"
              type="number"
              step="0.1"
              placeholder="98.6"
            />
          </div>

          <div class="form-group">
            <label for="pulse">Pulse (bpm)</label>
            <input
              id="pulse"
              v-model="patient.vitals.pulse"
              type="number"
              placeholder="Enter pulse rate"
            />
          </div>

          <div class="form-group">
            <label>Blood Pressure (mmHg)</label>
            <div class="blood-pressure-inputs">
              <input
                id="systolic"
                v-model="patient.vitals.bloodPressure.systolic"
                type="number"
                placeholder="Systolic"
              />
              <span class="bp-separator">/</span>
              <input
                id="diastolic"
                v-model="patient.vitals.bloodPressure.diastolic"
                type="number"
                placeholder="Diastolic"
              />
            </div>
          </div>
        </div>
      </section>

      <!-- Critical Symptoms Section -->
      <section class="form-section">
        <h3>Critical Symptoms</h3>
        <div class="form-group">
          <label>Select Critical Symptoms</label>
          <div class="checkbox-grid">
            <div v-for="symptom in criticalSymptoms" :key="symptom" class="checkbox-item">
              <input
                type="checkbox"
                :id="symptom"
                :value="symptom"
                v-model="patient.symptoms.selected"
              />
              <label :for="symptom">{{ symptom }}</label>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label for="symptomNotes">Additional Critical Notes</label>
          <textarea
            id="symptomNotes"
            v-model="patient.symptoms.notes"
            placeholder="Describe critical symptoms or concerns..."
            rows="3"
          ></textarea>
        </div>
      </section>

      <!-- Critical Allergies Section -->
      <section class="form-section">
        <h3>Critical Allergies</h3>
        <div class="form-group">
          <label>Select Critical Allergies</label>
          <div class="checkbox-grid">
            <div v-for="allergy in criticalAllergies" :key="allergy" class="checkbox-item">
              <input type="checkbox" :id="allergy" :value="allergy" v-model="patient.allergies" />
              <label :for="allergy">{{ allergy }}</label>
            </div>
          </div>
        </div>
      </section>

      <div v-if="error" class="error-message">{{ error }}</div>

      <button type="submit" class="submit-button" :disabled="loading">
        {{ loading ? 'Submitting...' : 'Submit High Priority Patient' }}
      </button>
    </form>

    <SuccessModal v-if="showSuccessModal" @close="closeSuccessModal" />
  </div>
</template>

<style scoped>
.page {
  padding: 2rem;
  text-align: center;
  max-width: 1200px;
  margin: 0 auto;
  font-size: 1.1rem;
}

.back-button {
  background-color: #dc2626;
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
  gap: 1.5rem;
  margin-top: 2rem;
  text-align: left;
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.form-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #dc2626;
}

.form-section h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #dc2626;
  font-size: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #fee2e2;
  border-radius: 4px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

label {
  font-weight: 600;
  color: #333;
  font-size: 1.2rem;
}

input {
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1.1rem;
  background: #f8f8f8;
}

input:focus {
  outline: none;
  border-color: #dc2626;
  background: white;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}

.submit-button {
  background-color: #dc2626;
  color: white;
  padding: 0.75rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.5rem;
  margin-top: 1rem;
  font-weight: 600;
}

.submit-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #dc2626;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.blood-pressure-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.bp-separator {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0 0.25rem;
  color: #666;
}

h2 {
  font-size: 2.5rem;
  margin-bottom: 1.5rem;
  color: #dc2626;
  font-weight: 700;
}

.priority-select {
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1.1rem;
  background: #f8f8f8;
  width: 100%;
  color: #dc2626;
  font-weight: 600;
}

.priority-select:focus {
  outline: none;
  border-color: #dc2626;
  background: white;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}

.priority-select option {
  font-weight: 600;
}

.priority-select option[value='1'] {
  color: #dc2626;
}

.priority-select option[value='2'] {
  color: #ea580c;
}

.priority-select option[value='3'] {
  color: #d97706;
}
</style>
