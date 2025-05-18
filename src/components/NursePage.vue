<script setup>
import { ref, onMounted, reactive } from 'vue'
// import SettingsModal from './SettingsModal.vue'
import draggable from 'vuedraggable'

// Emit events to parent component for navigation
const emit = defineEmits(['navigate'])

// Navigation handler to return to landing page
const goBack = () => {
  emit('navigate', 'landing')
}

// Settings modal state
// const showSettings = ref(false)

// Track drag state
const drag = ref(false)

// Status options
const statusOptions = [
  { value: 'waiting', label: 'Waiting' },
  { value: 'in-progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
]

// Priority options
const priorityOptions = [
  { value: 1, label: 'Priority 1 - Critical' },
  { value: 2, label: 'Priority 2 - High' },
  { value: 3, label: 'Priority 3 - Medium' },
  { value: 4, label: 'Priority 4 - Low' },
  { value: 5, label: 'Priority 5 - Routine' },
]

// Patient data state
const patients = ref([])
const loading = ref(true)
const error = ref(null)

// Edit state
const isEditing = ref(false)
const editedPatient = reactive({
  firstName: '',
  lastName: '',
  dateOfBirth: '',
  phoneNumber: '',
  status: 'waiting',
  priority: 3,
  notes: '',
  symptoms: {
    selected: [],
    notes: ''
  },
  vitals: {
    temperature: '',
    pulse: '',
    respirationRate: '',
    bloodPressure: {
      systolic: '',
      diastolic: ''
    }
  }
})

// Process patient data before displaying
const processPatientData = (patient) => {
  // Create a shallow copy to avoid modifying the original
  const processed = { ...patient }

  // Handle symptoms that might be in different formats
  if (typeof processed.symptoms === 'string') {
    // Legacy format - plain string
    processed.displaySymptoms = processed.symptoms
  } else if (processed.symptoms && typeof processed.symptoms === 'object') {
    // New format - object with selected and notes
    if (Array.isArray(processed.symptoms.selected) && processed.symptoms.selected.length > 0) {
      processed.displaySymptoms = processed.symptoms.selected.join(', ')
      if (processed.symptoms.notes) {
        processed.displaySymptoms += `. Notes: ${processed.symptoms.notes}`
      }
    } else if (processed.symptoms.notes) {
      processed.displaySymptoms = processed.symptoms.notes
    } else {
      processed.displaySymptoms = processed.symptom_text || 'No symptoms recorded'
    }
  } else if (processed.symptom_text) {
    // Fallback to symptom_text if available
    processed.displaySymptoms = processed.symptom_text
  } else {
    processed.displaySymptoms = 'No symptoms recorded'
  }

  // Ensure we have default values for essential fields
  processed.status = processed.status || 'waiting'
  processed.priority = processed.priority || 3

  return processed
}

// Fetch patients from API
const fetchPatients = async () => {
  try {
    loading.value = true
    const response = await fetch('http://localhost:3000/api/patients')
    if (!response.ok) throw new Error('Failed to fetch patients')
    const data = await response.json()
    patients.value = data.map(patient => {
      const processedPatient = {
        ...patient,
        id: patient._id || Math.random().toString(36).substr(2, 9), // Fallback ID if needed
        status: patient.status || 'waiting', // Default status if not set
        priority: patient.priority || 3 // Default priority if not set
      }
      return processPatientData(processedPatient)
    })
    // Sort by priority
    patients.value.sort((a, b) => a.priority - b.priority)
  } catch (err) {
    error.value = err.message
    console.error('Error fetching patients:', err)
  } finally {
    loading.value = false
  }
}

// Update patient in database
const updatePatient = async (patientId, updates) => {
  try {
    const response = await fetch(`http://localhost:3000/api/patients/${patientId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    })
    if (!response.ok) throw new Error('Failed to update patient')
    return await response.json()
  } catch (err) {
    console.error('Error updating patient:', err)
    throw err
  }
}

// Track currently selected patient for modal view
const selectedPatient = ref(null)

// Open patient detail modal
const openPatientDetail = (patient) => {
  selectedPatient.value = processPatientData(patient)
  isEditing.value = false
}

// Close patient detail modal
const closePatientDetail = () => {
  selectedPatient.value = null
  isEditing.value = false
}

// Start editing patient details
const startEditing = (patient) => {
  // Deep copy all fields to avoid direct binding
  editedPatient.firstName = patient.firstName || ''
  editedPatient.lastName = patient.lastName || ''
  editedPatient.dateOfBirth = patient.dateOfBirth || ''
  editedPatient.phoneNumber = patient.phoneNumber || ''
  editedPatient.status = patient.status || 'waiting'
  editedPatient.priority = patient.priority || 3
  editedPatient.notes = patient.notes || ''

  // Handle symptoms which might be in different formats
  if (typeof patient.symptoms === 'string') {
    // Legacy format - string only
    editedPatient.symptoms = {
      selected: patient.symptoms.split(',').map(s => s.trim()).filter(s => s !== ''),
      notes: ''
    }
  } else if (patient.symptoms && typeof patient.symptoms === 'object') {
    // New format - object with selected and notes
    if (Array.isArray(patient.symptoms.selected)) {
      editedPatient.symptoms.selected = [...patient.symptoms.selected]
    } else if (typeof patient.symptoms.selected === 'string') {
      editedPatient.symptoms.selected = patient.symptoms.selected.split(',').map(s => s.trim()).filter(s => s !== '')
    } else {
      editedPatient.symptoms.selected = []
    }
    editedPatient.symptoms.notes = patient.symptoms.notes || ''
  } else if (patient.symptom_text) {
    // Fallback to symptom_text
    editedPatient.symptoms = {
      selected: [],
      notes: patient.symptom_text
    }
  } else {
    editedPatient.symptoms = { selected: [], notes: '' }
  }

  // Handle vitals which might be in different formats
  if (patient.vitals && typeof patient.vitals === 'object') {
    // New format - object with all vitals
    editedPatient.vitals = {
      temperature: patient.vitals.temperature || '',
      pulse: patient.vitals.pulse || '',
      respirationRate: patient.vitals.respirationRate || '',
      bloodPressure: {
        systolic: (patient.vitals.bloodPressure?.systolic) || '',
        diastolic: (patient.vitals.bloodPressure?.diastolic) || ''
      }
    }
  } else {
    // Legacy format or missing data
    // Try to parse blood pressure if it exists as string (e.g. "120/80")
    let systolic = '', diastolic = ''
    if (patient.bloodPressure && typeof patient.bloodPressure === 'string') {
      const parts = patient.bloodPressure.split('/').map(v => v.trim())
      if (parts.length === 2) {
        [systolic, diastolic] = parts
      }
    }

    editedPatient.vitals = {
      temperature: patient.temperature || '',
      pulse: patient.pulse || '',
      respirationRate: patient.respirationRate || '',
      bloodPressure: {
        systolic: systolic,
        diastolic: diastolic
      }
    }
  }

  isEditing.value = true
}

// Save edited patient details
const saveEdits = async () => {
  if (!selectedPatient.value) return

  try {
    // Prepare updates based on form
    const updates = {
      firstName: editedPatient.firstName,
      lastName: editedPatient.lastName,
      dateOfBirth: editedPatient.dateOfBirth,
      phoneNumber: editedPatient.phoneNumber,
      status: editedPatient.status,
      priority: editedPatient.priority,
      notes: editedPatient.notes,
      symptoms: editedPatient.symptoms,
      vitals: editedPatient.vitals
    }

    // Save to database
    const response = await updatePatient(selectedPatient.value.id, updates)

    if (response.status === 'success') {
      // Simply reload all patients from the server to ensure consistency
      await fetchPatients()

      // Find the updated patient in the refreshed list and select it
      const updatedPatient = patients.value.find(p => p.id === selectedPatient.value.id)
      if (updatedPatient) {
        selectedPatient.value = updatedPatient
      }
    }

    // Reset edit mode
    isEditing.value = false
  } catch (err) {
    console.error('Failed to save changes:', err)
    // Could add error handling/notification here
  }
}

// Cancel editing
const cancelEditing = () => {
  isEditing.value = false
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
    case 4:
      return 'bg-green-100 text-green-800'
    case 5:
      return 'bg-purple-100 text-purple-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

// Notification state
const showNotification = ref(false)
const notificationMessage = ref('')
const pendingPriorityChange = ref(null)

// Handle drag end
const handleDragEnd = () => {
  drag.value = false
}

// Handle notification response
const handleNotificationResponse = () => {
  showNotification.value = false
  pendingPriorityChange.value = null
}

// Calculate time elapsed
const getTimeElapsed = (createdAt) => {
  const now = new Date()
  const created = new Date(createdAt)
  const diff = now - created

  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

// Format date
const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Format time
const formatTime = (time) => {
  if (!time) return 'N/A'
  return new Date(time).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Fetch patients on component mount
onMounted(() => {
  fetchPatients()
})
</script>

<template>
  <!-- Main container - takes full viewport height -->
  <div class="min-h-screen min-w-screen relative">
    <!-- Notification Box -->
    <Transition name="notification">
      <div
        v-if="showNotification"
        class="fixed right-4 top-4 bg-white rounded-lg shadow-lg p-4 w-80 border-l-4 border-blue-500 z-50"
      >
        <div class="flex items-start">
          <div class="flex-1">
            <p class="text-gray-800 font-medium">{{ notificationMessage }}</p>
          </div>
          <div class="flex gap-2 mt-4">
            <button
              @click="handleNotificationResponse(true)"
              class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              Confirm
            </button>
            <button
              @click="handleNotificationResponse(false)"
              class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Content wrapper with max width and padding -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header section with back button, title, and settings -->
      <div class="flex items-center mb-8">
        <button
          @click="goBack"
          class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          ← Back to Main
        </button>
        <h2 class="text-2xl font-bold text-gray-900 text-center w-full">Patient Management</h2>
        <!-- <button
          @click="showSettings = true"
          class="inline-flex items-center px-3 py-3 rounded-full hover:bg-gray-100 transition-colors"
          title="Settings"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6 text-gray-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
        </button> -->
      </div>
      <!-- Patient cards container -->
      <div class="flex flex-wrap gap-4 flex-col justify-center items-center">
        <!-- Loading state -->
        <div v-if="loading" class="w-full text-center py-8">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p class="text-gray-600">Loading patients...</p>
        </div>

        <!-- Error state -->
        <div v-else-if="error" class="w-full text-center py-8">
          <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <p>{{ error }}</p>
            <button
              @click="fetchPatients"
              class="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </div>

        <!-- Patient list -->
        <draggable
          v-else
          :list="patients"
          item-key="id"
          class="w-full"
          @start="drag = true"
          @end="handleDragEnd"
        >
          <template #item="{ element }">
            <div
              @click="openPatientDetail(element)"
              class="draggable-item bg-white rounded-lg shadow p-4 cursor-move hover:shadow-md transition-shadow flex-1 min-w-[40em] min-h-[10em] mb-4"
            >
              <!-- Card header with name and status -->
              <div class="flex justify-between items-start">
                <div>
                  <h3 class="text-lg font-semibold text-gray-900">
                    {{ element.firstName }} {{ element.lastName }}
                  </h3>
                  <p class="text-sm text-gray-500">
                    Check-in: {{ new Date(element.timeEntered).toLocaleTimeString() }}
                  </p>
                  <p class="text-sm text-gray-500">
                    Date: {{ new Date(element.dateOfVisit).toLocaleDateString() }}
                  </p>
                </div>

                <!-- Status badge -->
                <span
                  :class="[
                    getStatusColor(element.status),
                    'status-badge px-2 py-1 rounded-full text-xs font-medium',
                  ]"
                >
                  {{ element.status }}
                </span>
              </div>
              <!-- Priority badge -->
              <div class="mt-2">
                <span
                  :class="[
                    getPriorityColor(element.priority),
                    'priority-badge px-2 py-1 rounded-full text-xs font-medium',
                  ]"
                >
                  Priority {{ element.priority }}
                </span>
              </div>
              <!-- Symptoms preview -->
              <p class="mt-2 text-sm text-gray-600">{{ element.displaySymptoms }}</p>
            </div>
          </template>
        </draggable>
      </div>

      <!-- Patient Detail Modal -->
      <Transition name="modal">
        <div
          v-if="selectedPatient"
          class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50"
        >
          <!-- Modal content -->
          <div v-show="selectedPatient" class="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-y-auto p-8">
            <!-- Modal header with edit/close buttons -->
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-2xl font-bold text-gray-900">
                {{ isEditing ? 'Edit Patient Details' : 'Patient Details' }}
              </h2>
              <div class="flex gap-4">
                <!-- Edit mode buttons -->
                <template v-if="isEditing">
                  <button
                    @click="saveEdits"
                    class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
                  >
                    Save Changes
                  </button>
                  <button
                    @click="cancelEditing"
                    class="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50 transition"
                  >
                    Cancel
                  </button>
                </template>

                <!-- View mode buttons -->
                <template v-else>
                  <button
                    @click="startEditing(selectedPatient)"
                    class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
                  >
                    Edit
                  </button>
                  <button
                    @click="closePatientDetail"
                    class="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50 transition"
                  >
                    Close
                  </button>
                </template>
              </div>
            </div>

            <!-- Triage Information -->
            <div class="bg-gray-50 rounded-lg p-6 mb-8">
              <div class="flex justify-between items-start">
                <div>
                  <h2 class="text-2xl font-bold text-gray-900 mb-2">Triage Assessment</h2>
                  <div class="flex items-center gap-4">
                    <div v-if="!isEditing">
                      <span
                        :class="[
                          getPriorityColor(selectedPatient.priority),
                          'px-4 py-2 rounded-full text-lg font-medium'
                        ]"
                      >
                        ESI Level {{ selectedPatient.esi }}
                      </span>
                      <p class="text-gray-700 text-lg mt-2">{{ selectedPatient.esi_explanation }}</p>
                    </div>
                    <div v-else>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Priority Level</label>
                      <select
                        v-model="editedPatient.priority"
                        class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                      >
                        <option v-for="option in priorityOptions" :key="option.value" :value="option.value">
                          {{ option.label }}
                        </option>
                      </select>
                    </div>
                  </div>
                </div>
                <div class="text-right">
                  <p class="text-sm text-gray-500">Time Elapsed</p>
                  <p class="text-xl font-semibold text-gray-900">
                    {{ getTimeElapsed(selectedPatient.timeEntered) }}
                  </p>
                  <div v-if="isEditing" class="mt-4">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
                    <select
                      v-model="editedPatient.status"
                      class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option v-for="option in statusOptions" :key="option.value" :value="option.value">
                        {{ option.label }}
                      </option>
                    </select>
                  </div>
                  <div v-else class="mt-2">
                    <span
                      :class="[
                        getStatusColor(selectedPatient.status),
                        'px-3 py-1 rounded-full text-sm font-medium'
                      ]"
                    >
                      {{ selectedPatient.status }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Patient Information -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <!-- Left Column -->
              <div class="space-y-8">
                <!-- Personal Information -->
                <div>
                  <h3 class="text-xl font-semibold text-gray-900 mb-4">Personal Information</h3>
                  <div class="bg-gray-50 rounded-lg p-6 space-y-4">
                    <!-- View Mode -->
                    <div v-if="!isEditing" class="grid grid-cols-2 gap-4">
                      <div>
                        <p class="text-sm text-gray-500">First Name</p>
                        <p class="text-lg text-gray-900">{{ selectedPatient.firstName }}</p>
                      </div>
                      <div>
                        <p class="text-sm text-gray-500">Last Name</p>
                        <p class="text-lg text-gray-900">{{ selectedPatient.lastName }}</p>
                      </div>
                      <div>
                        <p class="text-sm text-gray-500">Date of Birth</p>
                        <p class="text-lg text-gray-900">{{ formatDate(selectedPatient.dateOfBirth) }}</p>
                      </div>
                      <div>
                        <p class="text-sm text-gray-500">Phone Number</p>
                        <p class="text-lg text-gray-900">{{ selectedPatient.phoneNumber }}</p>
                      </div>
                      <div class="col-span-2">
                        <p class="text-sm text-gray-500">Visit Information</p>
                        <p class="text-lg text-gray-900">
                          {{ formatDate(selectedPatient.dateOfVisit) }} at {{ formatTime(selectedPatient.timeEntered) }}
                        </p>
                      </div>
                    </div>

                    <!-- Edit Mode -->
                    <div v-else class="space-y-4">
                      <div class="grid grid-cols-2 gap-4">
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                          <input
                            type="text"
                            v-model="editedPatient.firstName"
                            class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                          />
                        </div>
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                          <input
                            type="text"
                            v-model="editedPatient.lastName"
                            class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                          />
                        </div>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
                          <input
                            type="date"
                            v-model="editedPatient.dateOfBirth"
                            class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                          />
                        </div>
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                          <input
                            type="tel"
                            v-model="editedPatient.phoneNumber"
                            class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Vitals -->
                <div>
                  <h3 class="text-xl font-semibold text-gray-900 mb-4">Vital Signs</h3>
                  <div class="bg-gray-50 rounded-lg p-6 space-y-4">
                    <!-- View Mode -->
                    <div v-if="!isEditing" class="grid grid-cols-2 gap-4">
                      <div>
                        <p class="text-sm text-gray-500">Temperature</p>
                        <p class="text-lg text-gray-900">
                          {{ selectedPatient.vitals?.temperature || 'N/A' }} °F
                        </p>
                      </div>
                      <div>
                        <p class="text-sm text-gray-500">Pulse</p>
                        <p class="text-lg text-gray-900">
                          {{ selectedPatient.vitals?.pulse || 'N/A' }} bpm
                        </p>
                      </div>
                      <div>
                        <p class="text-sm text-gray-500">Blood Pressure</p>
                        <p class="text-lg text-gray-900">
                          {{ selectedPatient.bloodPressure || selectedPatient.vitals?.bloodPressure || 'N/A' }}
                        </p>
                      </div>
                      <div>
                        <p class="text-sm text-gray-500">Respiration Rate</p>
                        <p class="text-lg text-gray-900">
                          {{ selectedPatient.vitals?.respirationRate || 'N/A' }} /min
                        </p>
                      </div>
                    </div>

                    <!-- Edit Mode -->
                    <div v-else class="space-y-4">
                      <div class="grid grid-cols-2 gap-4">
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">Temperature (°F)</label>
                          <input
                            type="number"
                            v-model="editedPatient.vitals.temperature"
                            class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                          />
                        </div>
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">Pulse (bpm)</label>
                          <input
                            type="number"
                            v-model="editedPatient.vitals.pulse"
                            class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                          />
                        </div>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">Blood Pressure</label>
                          <div class="flex gap-2 items-center">
                            <input
                              type="number"
                              v-model="editedPatient.vitals.bloodPressure.systolic"
                              placeholder="Systolic"
                              class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                            />
                            <span>/</span>
                            <input
                              type="number"
                              v-model="editedPatient.vitals.bloodPressure.diastolic"
                              placeholder="Diastolic"
                              class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                            />
                          </div>
                        </div>
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">Respiration Rate (/min)</label>
                          <input
                            type="number"
                            v-model="editedPatient.vitals.respirationRate"
                            class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Allergies -->
                <div>
                  <h3 class="text-xl font-semibold text-gray-900 mb-4">Allergies</h3>
                  <div class="bg-gray-50 rounded-lg p-6">
                    <div v-if="selectedPatient.allergies?.length" class="space-y-2">
                      <div v-for="allergy in selectedPatient.allergies" :key="allergy.name" class="p-2 bg-white rounded">
                        <p class="font-medium text-gray-900">{{ allergy.name }}</p>
                        <p class="text-sm text-gray-600">{{ allergy.reaction }}</p>
                      </div>
                    </div>
                    <p v-else class="text-gray-600">No known allergies</p>
                  </div>
                </div>
              </div>

              <!-- Right Column -->
              <div class="space-y-8">
                <!-- Current Symptoms -->
                <div>
                  <h3 class="text-xl font-semibold text-gray-900 mb-4">Current Symptoms</h3>
                  <div class="bg-gray-50 rounded-lg p-6">
                    <!-- View Mode -->
                    <div v-if="!isEditing && selectedPatient.symptoms">
                      <div v-if="typeof selectedPatient.symptoms === 'object'" class="space-y-4">
                        <div>
                          <p class="text-sm text-gray-500">Selected Symptoms</p>
                          <div class="flex flex-wrap gap-2 mt-2">
                            <span
                              v-for="symptom in selectedPatient.symptoms.selected"
                              :key="symptom"
                              class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                            >
                              {{ symptom }}
                            </span>
                          </div>
                        </div>
                        <div>
                          <p class="text-sm text-gray-500">Additional Notes</p>
                          <p class="text-lg text-gray-900 mt-1">{{ selectedPatient.symptoms.notes || 'None' }}</p>
                        </div>
                      </div>
                      <div v-else class="space-y-4">
                        <p class="text-lg text-gray-900">{{ selectedPatient.displaySymptoms }}</p>
                      </div>
                    </div>

                    <!-- Edit Mode -->
                    <div v-else-if="isEditing" class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Symptoms Description</label>
                        <textarea
                          v-model="editedPatient.symptoms.notes"
                          rows="4"
                          class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full resize-none"
                          placeholder="Describe symptoms in detail"
                        ></textarea>
                      </div>
                    </div>

                    <p v-else class="text-gray-600">No symptoms recorded</p>
                  </div>
                </div>

                <!-- Notes Section -->
                <div>
                  <h3 class="text-xl font-semibold text-gray-900 mb-4">Notes</h3>
                  <div class="bg-gray-50 rounded-lg p-6">
                    <div v-if="!isEditing">
                      <p class="text-lg text-gray-900">{{ selectedPatient.notes || 'No notes available' }}</p>
                    </div>
                    <div v-else>
                      <textarea
                        v-model="editedPatient.notes"
                        rows="6"
                        class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full resize-none"
                        placeholder="Add any additional notes here"
                      ></textarea>
                    </div>
                  </div>
                </div>

                <!-- Medications -->
                <div>
                  <h3 class="text-xl font-semibold text-gray-900 mb-4">Current Medications</h3>
                  <div class="bg-gray-50 rounded-lg p-6">
                    <div v-if="selectedPatient.medications?.length" class="space-y-2">
                      <div v-for="medication in selectedPatient.medications" :key="medication.name" class="p-2 bg-white rounded">
                        <p class="font-medium text-gray-900">{{ medication.name }}</p>
                        <p class="text-sm text-gray-600">
                          {{ medication.dosage }} - {{ medication.frequency }}
                        </p>
                      </div>
                    </div>
                    <p v-else class="text-gray-600">No current medications</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Settings Modal -->
      <!-- <SettingsModal :show="showSettings" @close="showSettings = false" /> -->
    </div>
  </div>
</template>

<style scoped>
/* Custom styles can be added here if needed */

textarea {
  resize: vertical;
  transition: all 0.2s ease;
}

textarea:focus {
  outline: none;
}

/* Card animations */
.draggable-item {
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.draggable-item:hover {
  transform: translateY(-2px);
}

.draggable-item.sortable-ghost {
  opacity: 0.5;
  background: #f3f4f6;
}

.draggable-item.sortable-chosen {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Modal animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-content-enter-active,
.modal-content-leave-active {
  transition: all 0.3s ease;
}

.modal-content-enter-from,
.modal-content-leave-to {
  transform: scale(0.95);
  opacity: 0;
}

/* Status badge animations */
.status-badge {
  transition: all 0.3s ease;
}

.status-badge:hover {
  transform: scale(1.05);
}

/* Priority badge animations */
.priority-badge {
  transition: all 0.3s ease;
}

.priority-badge:hover {
  transform: scale(1.05);
}

/* Notification animations */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from,
.notification-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* Google Places Autocomplete custom styles */
.pac-container {
  border-radius: 0.375rem;
  margin-top: 4px;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.pac-item {
  padding: 8px 12px;
  font-family: inherit;
}

.pac-item:hover {
  background-color: #f3f4f6;
}

.pac-item-selected {
  background-color: #e5e7eb;
}
</style>
