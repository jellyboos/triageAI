<script setup>
import { ref } from 'vue'
import SuccessModal from './SuccessModal.vue'

const emit = defineEmits(['navigate'])

const patient = ref({
  // Personal Information
  firstName: '',
  lastName: '',
  dateOfVisit: new Date().toISOString().split('T')[0],
  dateOfBirth: '',
  phoneNumber: '',

  // Medical Information/Vitals
  vitals: {
    temperature: '',
    pulse: '',
    respirationRate: '',
    bloodPressure: {
      systolic: '',
      diastolic: '',
    }
  },

  // Allergies and Medications
  allergies: {
    selected: [],
    other: ''
  },
  medications: {
    current: '',
  },

  // Medical History
  medicalHistory: {
    substanceUse: {
      alcohol: false,
      tobacco: false,
      recreationalDrugs: false
    },
    familyHistory: {
      selected: [],
      other: ''
    },
    surgeries: '',
    complications: ''
  },

  // Current Symptoms
  symptoms: {
    selected: [],
    notes: ''
  },

  // Images (if needed)
  images: []
})

// Common options for dropdowns
const commonAllergies = [
  'Penicillin',
  'Latex',
  'Peanuts',
  'Shellfish',
  'Dairy',
  'Eggs',
  'Soy',
  'Tree Nuts',
  'Wheat/Gluten'
]

const commonFamilyHistory = [
  'Heart Disease',
  'Diabetes',
  'Cancer',
  'High Blood Pressure',
  'Stroke',
  'Mental Health Conditions',
  'Asthma',
  'Arthritis'
]

const commonSymptoms = [
  'Fever',
  'Cough',
  'Shortness of breath',
  'Fatigue',
  'Headache',
  'Muscle aches',
  'Sore throat',
  'Loss of taste/smell',
  'Nausea',
  'Diarrhea'
]

const loading = ref(false)
const error = ref(null)
const showSuccessModal = ref(false)
const isDragging = ref(false)
const imageError = ref(null)

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
      body: JSON.stringify(patient.value)
    })

    if (!response.ok) {
      throw new Error(`Server responded with status: ${response.status}`)
    }

    const data = await response.json()
    showSuccessModal.value = true

    // Reset form with empty values but keep the structure
    patient.value = {
      firstName: '',
      lastName: '',
      dateOfVisit: new Date().toISOString().split('T')[0],
      dateOfBirth: '',
      phoneNumber: '',
      vitals: {
        temperature: '',
        pulse: '',
        respirationRate: '',
        bloodPressure: {
          systolic: '',
          diastolic: '',
        }
      },
      allergies: {
        selected: [],
        other: ''
      },
      medications: {
        current: '',
      },
      medicalHistory: {
        substanceUse: {
          alcohol: false,
          tobacco: false,
          recreationalDrugs: false
        },
        familyHistory: {
          selected: [],
          other: ''
        },
        surgeries: '',
        complications: ''
      },
      symptoms: {
        selected: [],
        notes: ''
      },
      images: []
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

const handleDragOver = (e) => {
  e.preventDefault()
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

const handleDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  const files = Array.from(e.dataTransfer.files)
  handleFiles(files)
}

const handleFileSelect = (e) => {
  const files = Array.from(e.target.files)
  handleFiles(files)
}

const handleFiles = (files) => {
  imageError.value = null
  const validFiles = files.filter((file) => {
    const isValid = file.type.startsWith('image/')
    if (!isValid) {
      imageError.value = 'Please upload only image files'
    }
    return isValid
  })

  validFiles.forEach((file) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      patient.value.images.push({
        name: file.name,
        data: e.target.result,
      })
    }
    reader.readAsDataURL(file)
  })
}

const removeImage = (index) => {
  patient.value.images.splice(index, 1)
}
</script>

<template>
  <div class="page">
    <button class="back-button" @click="goBack">← Back to Main</button>
    <h2>Patient Information</h2>

    <form @submit.prevent="submitForm" class="patient-form">
      <!-- Personal Information Section -->
      <section class="form-section">
        <h3>Personal Information</h3>
        <div class="form-grid">
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
            <label for="dateOfBirth">Date of Birth</label>
            <input
              id="dateOfBirth"
              v-model="patient.dateOfBirth"
              type="date"
              required
            />
          </div>

          <div class="form-group">
            <label for="phoneNumber">Phone Number</label>
            <input
              id="phoneNumber"
              v-model="patient.phoneNumber"
              type="tel"
              required
              placeholder="(XXX) XXX-XXXX"
            />
          </div>
        </div>
      </section>

      <!-- Vitals Section -->
      <section class="form-section">
        <h3>Medical Information/Vitals</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="temperature">Temperature (°F)</label>
            <input
              id="temperature"
              v-model="patient.vitals.temperature"
              type="number"
              step="0.1"
              required
              placeholder="98.6"
            />
          </div>

          <div class="form-group">
            <label for="pulse">Pulse (bpm)</label>
            <input
              id="pulse"
              v-model="patient.vitals.pulse"
              type="number"
              required
              placeholder="Enter pulse rate"
            />
          </div>

          <div class="form-group">
            <label for="respirationRate">Respiration Rate (breaths/min)</label>
            <input
              id="respirationRate"
              v-model="patient.vitals.respirationRate"
              type="number"
              required
              placeholder="Enter respiration rate"
            />
          </div>

          <div class="form-group">
            <label>Blood Pressure (mmHg)</label>
            <div class="blood-pressure-inputs">
              <input
                id="systolic"
                v-model="patient.vitals.bloodPressure.systolic"
                type="number"
                required
                placeholder="Systolic"
              />
              <span class="bp-separator">/</span>
              <input
                id="diastolic"
                v-model="patient.vitals.bloodPressure.diastolic"
                type="number"
                required
                placeholder="Diastolic"
              />
            </div>
          </div>
        </div>
      </section>

      <!-- Allergies and Medications Section -->
      <section class="form-section">
        <h3>Allergies and Medications</h3>

        <div class="form-group">
          <label>Known Allergies</label>
          <div class="checkbox-grid">
            <div v-for="allergy in commonAllergies" :key="allergy" class="checkbox-item">
              <input
                type="checkbox"
                :id="allergy"
                :value="allergy"
                v-model="patient.allergies.selected"
              />
              <label :for="allergy">{{ allergy }}</label>
            </div>
          </div>
          <input
            v-model="patient.allergies.other"
            type="text"
            placeholder="Other allergies..."
          />
        </div>

        <div class="form-group">
          <label for="medications">Current Medications</label>
          <textarea
            id="medications"
            v-model="patient.medications.current"
            placeholder="List all current medications..."
            rows="3"
          ></textarea>
        </div>
      </section>

      <!-- Medical History Section -->
      <section class="form-section">
        <h3>Medical History</h3>

        <div class="form-group">
          <label>Substance Use</label>
          <div class="checkbox-grid">
            <div class="checkbox-item">
              <input
                type="checkbox"
                id="alcohol"
                v-model="patient.medicalHistory.substanceUse.alcohol"
              />
              <label for="alcohol">Alcohol</label>
            </div>
            <div class="checkbox-item">
              <input
                type="checkbox"
                id="tobacco"
                v-model="patient.medicalHistory.substanceUse.tobacco"
              />
              <label for="tobacco">Tobacco</label>
            </div>
            <div class="checkbox-item">
              <input
                type="checkbox"
                id="recreationalDrugs"
                v-model="patient.medicalHistory.substanceUse.recreationalDrugs"
              />
              <label for="recreationalDrugs">Recreational Drugs</label>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>Family Health History</label>
          <div class="checkbox-grid">
            <div v-for="condition in commonFamilyHistory" :key="condition" class="checkbox-item">
              <input
                type="checkbox"
                :id="condition"
                :value="condition"
                v-model="patient.medicalHistory.familyHistory.selected"
              />
              <label :for="condition">{{ condition }}</label>
            </div>
          </div>
          <input
            v-model="patient.medicalHistory.familyHistory.other"
            type="text"
            placeholder="Other family health conditions..."
          />
        </div>

        <div class="form-group">
          <label for="surgeries">Previous Surgeries</label>
          <textarea
            id="surgeries"
            v-model="patient.medicalHistory.surgeries"
            placeholder="List any previous surgeries..."
            rows="3"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="complications">Health Complications</label>
          <textarea
            id="complications"
            v-model="patient.medicalHistory.complications"
            placeholder="List any health complications..."
            rows="3"
          ></textarea>
        </div>
      </section>

      <!-- Symptoms Section -->
      <section class="form-section">
        <h3>Current Symptoms</h3>

        <div class="form-group">
          <label>Common Symptoms</label>
          <div class="checkbox-grid">
            <div v-for="symptom in commonSymptoms" :key="symptom" class="checkbox-item">
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
          <label for="symptomNotes">Additional Symptoms/Notes</label>
          <textarea
            id="symptomNotes"
            v-model="patient.symptoms.notes"
            placeholder="Describe any other symptoms or concerns..."
            rows="3"
          ></textarea>
        </div>
      </section>

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
  max-width: 1200px;
  margin: 0 auto;
  animation: fadeIn 0.5s ease-out;
  font-size: 1.1rem;
}

.back-button {
  background-color: #666;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
}

.back-button:hover {
  background-color: #555;
  transform: translateX(-3px);
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
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
}

.patient-form:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.form-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-section h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #333;
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
  background: #f8f8f8;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.checkbox-item:hover {
  background: #f0f0f0;
  transform: translateX(3px);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: transform 0.3s ease;
}

.form-group:focus-within {
  transform: translateX(5px);
}

label {
  font-weight: 600;
  color: #333;
  transition: color 0.3s ease;
  font-size: 1.2rem;
}

.form-group:focus-within label {
  color: #4caf50;
}

input {
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  background: #f8f8f8;
}

input:focus {
  outline: none;
  border-color: #4caf50;
  background: white;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.submit-button {
  background-color: #4caf50;
  color: white;
  padding: 0.75rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 1rem;
  transition: all 0.3s ease;
  font-weight: 600;
}

.submit-button:hover:not(:disabled) {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2);
}

.submit-button:active:not(:disabled) {
  transform: translateY(0);
}

.submit-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.error-message {
  color: #ff0000;
  margin-top: 1rem;
  font-size: 0.9rem;
  animation: shake 0.5s ease-in-out;
}

.blood-pressure-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: transform 0.3s ease;
}

.blood-pressure-inputs:focus-within {
  transform: translateX(5px);
}

.bp-separator {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0 0.25rem;
  color: #666;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shake {
  0%,
  100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

h2 {
  font-size: 2.5rem;
  margin-bottom: 1.5rem;
  color: #333;
  font-weight: 700;
}
</style>

