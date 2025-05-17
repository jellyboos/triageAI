<script setup>
import { ref } from 'vue'

// Emit events to parent component for navigation
const emit = defineEmits(['navigate'])

// Navigation handler to return to landing page
const goBack = () => {
  emit('navigate', 'landing')
}

// Mock patient data - in real app, this would come from an API
const patients = ref([
  {
    id: 1,
    name: 'John Doe',
    checkInTime: '2024-03-20T10:30:00',
    status: 'waiting',
    priority: 2,
    symptoms: 'Fever, Cough',
    notes: 'Patient reports high fever for 2 days',
  },
  {
    id: 2,
    name: 'Jane Smith',
    checkInTime: '2024-03-20T10:45:00',
    status: 'in-progress',
    priority: 1,
    symptoms: 'Chest Pain',
    notes: 'Severe chest pain, needs immediate attention',
  },
  {
    id: 3,
    name: 'Mike Johnson',
    checkInTime: '2024-03-20T11:00:00',
    status: 'waiting',
    priority: 3,
    symptoms: 'Headache',
    notes: 'Mild headache, no other symptoms',
  },
])

// Track currently selected patient for modal view
const selectedPatient = ref(null)

// Open patient detail modal
const openPatientDetail = (patient) => {
  selectedPatient.value = patient
}

// Close patient detail modal
const closePatientDetail = () => {
  selectedPatient.value = null
}

// Return appropriate Tailwind classes based on patient status
const getStatusColor = (status) => {
  switch (status) {
    case 'waiting':
      return 'bg-yellow-100 text-yellow-800'
    case 'in-progress':
      return 'bg-blue-100 text-blue-800'
    case 'completed':
      return 'bg-green-100 text-green-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

// Return appropriate Tailwind classes based on priority level
const getPriorityColor = (priority) => {
  switch (priority) {
    case 1:
      return 'bg-red-100 text-red-800'
    case 2:
      return 'bg-orange-100 text-orange-800'
    case 3:
      return 'bg-yellow-100 text-yellow-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}
</script>

<template>
  <!-- Main container - takes full viewport height -->
  <div class="min-h-screen min-w-screen">
    <!-- Content wrapper with max width and padding -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header section with back button and title -->
      <div class="flex justify-between items-center mb-8">
        <button
          @click="goBack"
          class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          ← Back to Main
        </button>
        <h2 class="text-2xl font-bold text-gray-900">Patient Management</h2>
      </div>

      <!-- Patient cards container - uses flexbox with wrapping -->
      <div class="flex flex-wrap gap-4 flex-col">
        <!-- Individual patient card -->
        <div
          v-for="patient in patients"
          :key="patient.id"
          @click="openPatientDetail(patient)"
          class="bg-white rounded-lg shadow p-4 cursor-pointer hover:shadow-md transition-shadow flex-1 min-w-[300px] max-w-[400px]"
        >
          <!-- Card header with name and status -->
          <div class="flex justify-between items-start">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">{{ patient.name }}</h3>
              <p class="text-sm text-gray-500">
                Check-in: {{ new Date(patient.checkInTime).toLocaleTimeString() }}
              </p>
            </div>
            <!-- Status badge -->
            <span
              :class="[
                getStatusColor(patient.status),
                'px-2 py-1 rounded-full text-xs font-medium',
              ]"
            >
              {{ patient.status }}
            </span>
          </div>
          <!-- Priority badge -->
          <div class="mt-2">
            <span
              :class="[
                getPriorityColor(patient.priority),
                'px-2 py-1 rounded-full text-xs font-medium',
              ]"
            >
              Priority {{ patient.priority }}
            </span>
          </div>
          <!-- Symptoms preview -->
          <p class="mt-2 text-sm text-gray-600">{{ patient.symptoms }}</p>
        </div>
      </div>

      <!-- Patient Detail Modal - appears when a patient is selected -->
      <div
        v-if="selectedPatient"
        class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4"
      >
        <!-- Modal content -->
        <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
          <!-- Modal header with close button -->
          <div class="flex justify-between items-start">
            <h3 class="text-xl font-bold text-gray-900">{{ selectedPatient.name }}</h3>
            <button @click="closePatientDetail" class="text-gray-400 hover:text-gray-500">
              <span class="sr-only">Close</span>
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <!-- Modal body with patient details -->
          <div class="mt-4 space-y-4">
            <!-- Check-in time -->
            <div>
              <h4 class="text-sm font-medium text-gray-500">Check-in Time</h4>
              <p class="mt-1 text-sm text-gray-900">
                {{ new Date(selectedPatient.checkInTime).toLocaleString() }}
              </p>
            </div>

            <!-- Status -->
            <div>
              <h4 class="text-sm font-medium text-gray-500">Status</h4>
              <span
                :class="[
                  getStatusColor(selectedPatient.status),
                  'mt-1 px-2 py-1 rounded-full text-xs font-medium',
                ]"
              >
                {{ selectedPatient.status }}
              </span>
            </div>

            <!-- Priority -->
            <div>
              <h4 class="text-sm font-medium text-gray-500">Priority</h4>
              <span
                :class="[
                  getPriorityColor(selectedPatient.priority),
                  'mt-1 px-2 py-1 rounded-full text-xs font-medium',
                ]"
              >
                Priority {{ selectedPatient.priority }}
              </span>
            </div>

            <!-- Symptoms -->
            <div>
              <h4 class="text-sm font-medium text-gray-500">Symptoms</h4>
              <p class="mt-1 text-sm text-gray-900">{{ selectedPatient.symptoms }}</p>
            </div>

            <!-- Notes -->
            <div>
              <h4 class="text-sm font-medium text-gray-500">Notes</h4>
              <p class="mt-1 text-sm text-gray-900">{{ selectedPatient.notes }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom styles can be added here if needed */
</style>
