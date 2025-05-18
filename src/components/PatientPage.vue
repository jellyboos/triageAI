<script setup>
import { ref } from 'vue'
import SuccessModal from './SuccessModal.vue'

const emit = defineEmits(['navigate'])

const patient = ref({
  firstName: '',
  lastName: '',
  age: '',
  bloodPressure: {
    systolic: '',
    diastolic: '',
  },
  symptoms: {
    selected: [],
    notes: '',
  },
  images: [],
})

const loading = ref(false)
const error = ref(null)
const showSuccessModal = ref(false)
const isDragging = ref(false)
const imageError = ref(null)

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
  'Diarrhea',
]

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
      bloodPressure: {
        systolic: '',
        diastolic: '',
      },
      symptoms: {
        selected: [],
        notes: '',
      },
      images: [],
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

      <div class="form-group">
        <label>Blood Pressure</label>
        <div class="bp-note">Please obtain blood pressure with nurse</div>
        <div class="blood-pressure-inputs">
          <div class="bp-input">
            <input
              id="systolic"
              v-model="patient.bloodPressure.systolic"
              type="number"
              required
              min="60"
              max="250"
              placeholder="Systolic"
            />
            <span class="bp-separator">/</span>
          </div>
          <div class="bp-input">
            <input
              id="diastolic"
              v-model="patient.bloodPressure.diastolic"
              type="number"
              required
              min="40"
              max="150"
              placeholder="Diastolic"
            />
          </div>
          <span class="bp-unit">mmHg</span>
        </div>
      </div>

      <div class="form-group">
        <label>Symptoms</label>
        <div class="symptoms-container">
          <div class="symptoms-grid">
            <div v-for="symptom in commonSymptoms" :key="symptom" class="symptom-checkbox">
              <input
                type="checkbox"
                :id="symptom"
                :value="symptom"
                v-model="patient.symptoms.selected"
              />
              <label :for="symptom">{{ symptom }}</label>
            </div>
          </div>
          <div class="symptoms-notes">
            <label for="symptomsNotes">Additional Notes</label>
            <textarea
              id="symptomsNotes"
              v-model="patient.symptoms.notes"
              placeholder="Describe any other symptoms or concerns..."
              rows="3"
            ></textarea>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label>Medical Images</label>
        <div
          class="image-upload-area"
          :class="{ dragging: isDragging }"
          @dragover="handleDragOver"
          @dragleave="handleDragLeave"
          @drop="handleDrop"
        >
          <input
            type="file"
            id="imageUpload"
            accept="image/*"
            multiple
            @change="handleFileSelect"
            class="file-input"
          />
          <div class="upload-content">
            <div class="upload-icon">📁</div>
            <p>Drag & drop images here or click to select</p>
            <p class="upload-hint">Supports: JPG, PNG, GIF</p>
          </div>
        </div>

        <div v-if="imageError" class="error-message">{{ imageError }}</div>

        <div v-if="patient.images.length > 0" class="image-preview-grid">
          <div v-for="(image, index) in patient.images" :key="index" class="image-preview">
            <img :src="image.data" :alt="image.name" />
            <button class="remove-image" @click="removeImage(index)">×</button>
            <span class="image-name">{{ image.name }}</span>
          </div>
        </div>
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
  max-width: 800px;
  margin: 0 auto;
  animation: fadeIn 0.5s ease-out;
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

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  transition: transform 0.3s ease;
}

.form-group:focus-within {
  transform: translateX(5px);
}

label {
  font-weight: 600;
  color: #333;
  transition: color 0.3s ease;
}

.form-group:focus-within label {
  color: #4caf50;
}

input {
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
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

.bp-input {
  display: flex;
  align-items: center;
}

.bp-input input {
  width: 80px;
}

.bp-separator {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0 0.25rem;
  color: #666;
}

.bp-unit {
  color: #666;
  font-size: 0.9rem;
}

.bp-note {
  color: #666;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
  font-style: italic;
  transition: color 0.3s ease;
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

.symptoms-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.symptoms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
}

.symptom-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f8f8f8;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.symptom-checkbox:hover {
  background: #f0f0f0;
  transform: translateX(3px);
}

.symptom-checkbox input[type='checkbox'] {
  width: auto;
  margin: 0;
}

.symptom-checkbox label {
  font-weight: normal;
  margin: 0;
  cursor: pointer;
}

.symptoms-notes {
  margin-top: 1rem;
}

textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: all 0.3s ease;
  background: #f8f8f8;
}

textarea:focus {
  outline: none;
  border-color: #4caf50;
  background: white;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.image-upload-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8f8f8;
  position: relative;
}

.image-upload-area.dragging {
  border-color: #4caf50;
  background: rgba(76, 175, 80, 0.1);
}

.file-input {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  opacity: 0;
  cursor: pointer;
}

.upload-content {
  pointer-events: none;
}

.upload-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.upload-hint {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.5rem;
}

.image-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.image-preview {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.image-preview:hover {
  transform: translateY(-2px);
}

.image-preview img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  display: block;
}

.remove-image {
  position: absolute;
  top: 5px;
  right: 5px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  cursor: pointer;
  font-size: 1.2rem;
  color: #ff4444;
  transition: all 0.3s ease;
}

.remove-image:hover {
  background: #ff4444;
  color: white;
}

.image-name {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
