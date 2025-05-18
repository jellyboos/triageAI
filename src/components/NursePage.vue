<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
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
  { value: 'waiting', label: 'Processing' },
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

// Reference options for multi-select fields
const symptomOptions = ref([])
const allergyOptions = ref([])
const substanceUseOptions = ref([])
const familyHistoryOptions = ref([])

// Fetch options from API
const fetchOptions = async () => {
  try {
    const categories = ['symptoms', 'allergies', 'substance_use', 'family_history']
    const promises = categories.map((category) =>
      fetch(`http://localhost:3000/api/options/${category}`).then((response) => response.json()),
    )

    const results = await Promise.all(promises)

    // Assign options to respective arrays
    results.forEach((result, index) => {
      if (result.status === 'success') {
        switch (categories[index]) {
          case 'symptoms':
            symptomOptions.value = result.options
            break
          case 'allergies':
            allergyOptions.value = result.options
            break
          case 'substance_use':
            substanceUseOptions.value = result.options
            break
          case 'family_history':
            familyHistoryOptions.value = result.options
            break
        }
      }
    })
  } catch (err) {
    console.error('Error fetching options:', err)
  }
}

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
    notes: '',
  },
  vitals: {
    temperature: '',
    pulse: '',
    respirationRate: '',
    bloodPressure: {
      systolic: '',
      diastolic: '',
    },
  },
  // Add new multi-select fields
  allergies: [],
  substance_use: [],
  family_history: [],
  treatmentPlan: '',
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
    patients.value = data.map((patient) => {
      const processedPatient = {
        ...patient,
        id: patient._id || Math.random().toString(36).substr(2, 9), // Fallback ID if needed
        status: patient.status || 'waiting', // Default status if not set
        priority: patient.priority || 3, // Default priority if not set
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
      selected: patient.symptoms
        .split(',')
        .map((s) => s.trim())
        .filter((s) => s !== ''),
      notes: '',
    }
  } else if (patient.symptoms && typeof patient.symptoms === 'object') {
    // New format - object with selected and notes
    if (Array.isArray(patient.symptoms.selected)) {
      editedPatient.symptoms.selected = [...patient.symptoms.selected]
    } else if (typeof patient.symptoms.selected === 'string') {
      editedPatient.symptoms.selected = patient.symptoms.selected
        .split(',')
        .map((s) => s.trim())
        .filter((s) => s !== '')
    } else {
      editedPatient.symptoms.selected = []
    }
    editedPatient.symptoms.notes = patient.symptoms.notes || ''
  } else if (patient.symptom_text) {
    // Fallback to symptom_text
    editedPatient.symptoms = {
      selected: [],
      notes: patient.symptom_text,
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
        systolic: patient.vitals.bloodPressure?.systolic || '',
        diastolic: patient.vitals.bloodPressure?.diastolic || '',
      },
    }
  } else {
    // Legacy format or missing data
    // Try to parse blood pressure if it exists as string (e.g. "120/80")
    let systolic = '',
      diastolic = ''
    if (patient.bloodPressure && typeof patient.bloodPressure === 'string') {
      const parts = patient.bloodPressure.split('/').map((v) => v.trim())
      if (parts.length === 2) {
        ;[systolic, diastolic] = parts
      }
    }

    editedPatient.vitals = {
      temperature: patient.temperature || '',
      pulse: patient.pulse || '',
      respirationRate: patient.respirationRate || '',
      bloodPressure: {
        systolic: systolic,
        diastolic: diastolic,
      },
    }
  }

  // Handle multi-select fields
  editedPatient.allergies = Array.isArray(patient.allergies) ? [...patient.allergies] : []
  editedPatient.substance_use = Array.isArray(patient.substance_use)
    ? [...patient.substance_use]
    : []
  editedPatient.family_history = Array.isArray(patient.family_history)
    ? [...patient.family_history]
    : []

  // Handle multi-select fields
  editedPatient.allergies = Array.isArray(patient.allergies) ? [...patient.allergies] : []
  editedPatient.substance_use = Array.isArray(patient.substance_use)
    ? [...patient.substance_use]
    : []
  editedPatient.family_history = Array.isArray(patient.family_history)
    ? [...patient.family_history]
    : []

  // Handle treatment plan
  editedPatient.treatmentPlan = patient.treatmentPlan || ''

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
      vitals: editedPatient.vitals,
      allergies: editedPatient.allergies,
      substance_use: editedPatient.substance_use,
      family_history: editedPatient.family_history,
      treatmentPlan: editedPatient.treatmentPlan,
    }

    // Save to database
    const response = await updatePatient(selectedPatient.value.id, updates)

    if (response.status === 'success') {
      // Simply reload all patients from the server to ensure consistency
      await fetchPatients()

      // Find the updated patient in the refreshed list and select it
      const updatedPatient = patients.value.find((p) => p.id === selectedPatient.value.id)
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

// Get display text for status
const getStatusLabel = (status) => {
  const option = statusOptions.find((opt) => opt.value === status)
  return option ? option.label : status
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

// Return appropriate Tailwind classes for patient card background based on priority
const getPriorityCardBackground = (priority) => {
  switch (priority) {
    case 1:
      return 'bg-red-50' // Light pastel red
    case 2:
      return 'bg-orange-50' // Light pastel orange
    case 3:
      return 'bg-yellow-50' // Light pastel yellow
    case 4:
      return 'bg-blue-50' // Light pastel blue
    case 5:
      return 'bg-green-50' // Light pastel green
    default:
      return 'bg-gray-50' // Default pastel gray for any other cases
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
    day: 'numeric',
  })
}

// Format time
const formatTime = (time) => {
  if (!time) return 'N/A'
  return new Date(time).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Call on component mount
onMounted(() => {
  fetchPatients()
  fetchOptions()
})

// Call on component mount
onMounted(() => {
  fetchBusynessPrediction()
})

// Add busyness prediction state
const busynessData = ref({
  predictedPatients: null,
  date: null,
  timezone: null,
  error: null,
})

// Add function to fetch busyness prediction
const fetchBusynessPrediction = async () => {
  try {
    const response = await fetch('http://localhost:3000/api/predict/busyness')
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    console.log('API Response:', data)

    // Handle the predictions array structure
    const prediction = data.predictions[0] // Get first prediction from array
    busynessData.value = {
      predictedPatients: prediction.predicted_busyness,
      date: prediction.date,
      timezone: null,
      error: null,
    }
  } catch (error) {
    console.error('Error fetching busyness prediction:', error)
    busynessData.value = {
      predictedPatients: null,
      date: null,
      timezone: null,
      error: error.message || 'Unable to fetch prediction',
    }
  }
}

// Add current active tab state
const activeTab = ref('all')

// Filter patients by status
const filteredPatients = computed(() => {
  if (activeTab.value === 'all') {
    return patients.value
  }
  return patients.value.filter((patient) => patient.status === activeTab.value)
})

// Count patients by status
const patientCounts = computed(() => {
  const counts = {
    all: patients.value.length,
    waiting: 0,
    'in-progress': 0,
    completed: 0,
  }

  patients.value.forEach((patient) => {
    if (Object.prototype.hasOwnProperty.call(counts, patient.status)) {
      counts[patient.status]++
    }
  })

  return counts
})

// Quick status update function
const updatePatientStatus = async (patient, newStatus) => {
  try {
    // Prepare updates with only the status field
    const updates = {
      status: newStatus,
    }

    // Save to database
    const response = await updatePatient(patient.id, updates)

    if (response.status === 'success') {
      // Reload all patients from the server to ensure consistency
      await fetchPatients()
    }
  } catch (err) {
    console.error('Failed to update patient status:', err)
  }
}

// State for emergency rooms modal
const showEmergencyRoomsModal = ref(false)
const emergencyRoomsData = ref([])
const loadingEmergencyRooms = ref(false)
const errorEmergencyRooms = ref(null)

// Add state for selected hospital and map query
const selectedRelocationHospital = ref(null)
const mapQuery = ref('')

// Fetch emergency rooms
const fetchEmergencyRooms = async () => {
  loadingEmergencyRooms.value = true
  errorEmergencyRooms.value = null
  selectedRelocationHospital.value = null // Reset selection
  try {
    const response = await fetch('http://localhost:3000/api/emergency-rooms')
    if (!response.ok) {
      throw new Error('Failed to fetch emergency rooms')
    }
    const data = await response.json()

    let processedRooms = []
    if (data.status === 'success' && Array.isArray(data.emergency_rooms)) {
      processedRooms = data.emergency_rooms
    } else if (Array.isArray(data)) {
      processedRooms = data
    } else {
      console.warn('Emergency rooms data might not be in the expected array format:', data)
      errorEmergencyRooms.value =
        data.message || 'Received data is not in the expected array format or is empty.'
    }

    // Filter for objects with at least a name property, or strings
    emergencyRoomsData.value = processedRooms
      .map((room) => {
        if (typeof room === 'string') return { name: room, vicinity: '' } // Convert strings to basic objects
        if (typeof room === 'object' && room !== null && room.name) return room
        return null
      })
      .filter((room) => room !== null)

    if (emergencyRoomsData.value.length > 0) {
      // Set initial map query to the first hospital or a general area
      mapQuery.value = emergencyRoomsData.value[0].vicinity
        ? `${emergencyRoomsData.value[0].name}, ${emergencyRoomsData.value[0].vicinity}`
        : emergencyRoomsData.value[0].name
    } else {
      mapQuery.value = 'United States' // Default if no rooms
      if (!errorEmergencyRooms.value) {
        // errorEmergencyRooms.value = "No emergency rooms found after processing."; // Optionally set error
        console.warn('Processed emergency rooms data is empty.')
      }
    }
  } catch (err) {
    console.error('Error fetching emergency rooms:', err)
    errorEmergencyRooms.value = err.message
    emergencyRoomsData.value = []
    mapQuery.value = 'United States' // Default on error
  } finally {
    loadingEmergencyRooms.value = false
  }
}

// Open emergency rooms modal
const openRelocateModal = () => {
  fetchEmergencyRooms() // Fetch data when modal is opened
  showEmergencyRoomsModal.value = true
}

// Close emergency rooms modal
const closeRelocateModal = () => {
  showEmergencyRoomsModal.value = false
  emergencyRoomsData.value = []
  errorEmergencyRooms.value = null
  selectedRelocationHospital.value = null // Reset selected hospital
  mapQuery.value = '' // Reset map query
}

// Select a hospital for relocation
const selectHospitalForRelocation = (hospital) => {
  selectedRelocationHospital.value = hospital
  // Use name and vicinity for a more specific map query if available
  if (hospital && hospital.name && hospital.vicinity) {
    mapQuery.value = `${hospital.name}, ${hospital.vicinity}`
  } else if (hospital && hospital.name) {
    mapQuery.value = hospital.name
  } else {
    // Fallback if hospital object or its properties are not as expected
    mapQuery.value = 'United States' // Default query
  }
}

// Confirm patient relocation
const confirmPatientRelocation = async () => {
  if (!selectedRelocationHospital.value || !selectedPatient.value) {
    console.error('No hospital selected or patient details missing.')
    // Optionally show a user-facing error notification here
    notificationMessage.value = 'Please select a hospital first.'
    showNotification.value = true // Assuming you have a general notification system
    // Hide notification after a few seconds
    setTimeout(() => {
      showNotification.value = false
    }, 3000)
    return
  }

  try {
    const patientId = selectedPatient.value.id
    const response = await fetch(`http://localhost:3000/api/patients/${patientId}/relocate`, {
      method: 'DELETE',
    })

    const responseData = await response.json()

    if (response.ok && responseData.status === 'success') {
      notificationMessage.value = `Patient ${selectedPatient.value.firstName} ${selectedPatient.value.lastName} relocated successfully.`
      showNotification.value = true
      setTimeout(() => {
        showNotification.value = false
      }, 4000)

      await fetchPatients() // Refresh the main patient list
      closeRelocateModal() // Close the relocation modal
      closePatientDetail() // Close the patient detail modal as patient is gone
    } else {
      throw new Error(responseData.message || 'Failed to relocate patient')
    }
  } catch (err) {
    console.error('Error relocating patient:', err)
    notificationMessage.value = `Error: ${err.message}`
    showNotification.value = true
    setTimeout(() => {
      showNotification.value = false
    }, 5000)
    errorEmergencyRooms.value = err.message // Display error in the relocate modal too if needed
  }
}

// Add computed property for Google Maps Embed URL
const googleMapsEmbedUrl = computed(() => {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY
  const baseUrl = 'https://www.google.com/maps/embed/v1/search'
  // Use a default query if mapQuery is empty to prevent errors with encodeURIComponent
  const queryValue = encodeURIComponent(mapQuery.value || 'United States')

  if (apiKey) {
    return `${baseUrl}?key=${apiKey}&q=${queryValue}`
  } else {
    // If no API key, Google Maps Embed API will likely show an error or have limited functionality.
    // It's better than breaking the app if the key is momentarily missing during setup.
    console.warn(
      'Google Maps API Key (VITE_GOOGLE_MAPS_API_KEY) is not set in .env file. Map functionality will be limited or show an error.',
    )
    return `${baseUrl}?q=${queryValue}`
  }
})
</script>

<template>
  <!-- Main container - takes full viewport height -->
  <div class="min-h-screen min-w-screen relative bg-gray-50">
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
      <div class="bg-white rounded-xl shadow-md mb-8 p-4">
        <div class="flex items-center justify-between">
          <button
            @click="goBack"
            class="inline-flex items-center px-4 py-2 border border-gray-200 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-all duration-200 hover:shadow-md"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5 mr-2"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
                clip-rule="evenodd"
              />
            </svg>
            Back to Main
          </button>

          <h2
            class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent"
          >
            Patient Management
          </h2>

          <div class="flex items-center gap-4">
            <button
              @click="emit('navigate', 'high-priority')"
              class="inline-flex items-center px-4 py-2 border border-red-200 rounded-lg shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 transition-all duration-200 hover:shadow-md"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5 mr-2"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fill-rule="evenodd"
                  d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                  clip-rule="evenodd"
                />
              </svg>
              Add High Priority Patient
            </button>

            <div
              class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-3 border border-blue-100 shadow-sm"
            >
              <div class="text-sm text-blue-600 font-medium">
                {{ busynessData.date || 'Loading...' }}
              </div>
              <div class="text-lg font-bold text-blue-700">
                <template v-if="busynessData.error">
                  <span class="text-red-600">{{ busynessData.error }}</span>
                  'px-4 py-2 rounded-lg font-medium transition-colors',
                </template>
                <template v-else>
                  {{ busynessData.predictedPatients || '--' }} patients expected
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- Tab Navigation -->
      <div class="bg-white rounded-xl shadow-md mb-6 p-4">
        <div class="flex justify-center space-x-4">
          <button
            @click="activeTab = 'all'"
            :class="[
              activeTab === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
            ]"
          >
            All Patients ({{ patientCounts.all }})
          </button>
          <button
            @click="activeTab = 'waiting'"
            :class="[
              'px-4 py-2 rounded-lg font-medium transition-colors',
              activeTab === 'waiting'
                ? 'bg-yellow-500 text-white'
                : 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100',
            ]"
          >
            Processing ({{ patientCounts.waiting }})
          </button>
          <button
            @click="activeTab = 'in-progress'"
            :class="[
              'px-4 py-2 rounded-lg font-medium transition-colors',
              activeTab === 'in-progress'
                ? 'bg-blue-500 text-white'
                : 'bg-blue-50 text-blue-700 hover:bg-blue-100',
            ]"
          >
            In Progress ({{ patientCounts['in-progress'] }})
          </button>
          <button
            @click="activeTab = 'completed'"
            :class="[
              'px-4 py-2 rounded-lg font-medium transition-colors',
              activeTab === 'completed'
                ? 'bg-green-500 text-white'
                : 'bg-green-50 text-green-700 hover:bg-green-100',
            ]"
          >
            Completed ({{ patientCounts.completed }})
          </button>
        </div>
      </div>
      <!-- Patient cards container -->
      <div class="flex flex-wrap gap-4 flex-col justify-center items-center">
        <!-- Loading state -->
        <div v-if="loading" class="w-full text-center py-8">
          <div
            class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"
          ></div>
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

        <!-- Empty state for filtered results -->
        <div v-else-if="filteredPatients.length === 0" class="w-full text-center py-8">
          <div
            class="bg-gray-50 border border-gray-200 text-gray-700 px-6 py-8 rounded-lg shadow-sm"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-12 w-12 mx-auto text-gray-400 mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 class="text-xl font-medium text-gray-900 mb-2">No patients found</h3>
            <p class="text-gray-600 mb-4">
              There are no patients in the "{{ getStatusLabel(activeTab) }}" status category.
            </p>
            <button
              @click="activeTab = 'all'"
              class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              View All Patients
            </button>
          </div>
        </div>

        <!-- Patient list -->
        <draggable
          v-else
          :list="filteredPatients"
          item-key="id"
          class="w-full"
          @start="drag = true"
          @end="handleDragEnd"
        >
          <template #item="{ element }">
            <div
              @click="openPatientDetail(element)"
              :class="[
                'draggable-item',
                'rounded-2xl',
                'shadow',
                'p-4',
                'cursor-move',
                'hover:shadow-md',
                'transition-shadow',
                'flex-1',
                'min-w-[40em]',
                'min-h-[10em]',
                'mb-4',
                getPriorityCardBackground(element.priority),
              ]"
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

                <!-- Status controls -->
                <div>
                  <!-- Status badge -->
                  <span
                    :class="[
                      getStatusColor(element.status),
                      'status-badge px-2 py-1 rounded-full text-xs font-medium mb-2 inline-block',
                    ]"
                  >
                    {{ getStatusLabel(element.status) }}
                  </span>

                  <!-- Quick status change dropdown -->
                  <div class="mt-2">
                    <select
                      :value="element.status"
                      @change="updatePatientStatus(element, $event.target.value)"
                      class="text-xs border border-gray-300 rounded p-1"
                      @click.stop
                    >
                      <option disabled>Change Status</option>
                      <option
                        v-for="option in statusOptions"
                        :key="option.value"
                        :value="option.value"
                      >
                        {{ option.label }}
                      </option>
                    </select>
                  </div>
                </div>
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
          <div
            v-show="selectedPatient"
            v-if="selectedPatient"
            class="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-y-auto p-8"
          >
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
                    @click="openRelocateModal"
                    class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition"
                  >
                    Relocate Patient
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
                          'px-4 py-2 rounded-full text-lg font-medium',
                        ]"
                      >
                        Priority {{ selectedPatient.priority }}
                      </span>
                      <p class="text-gray-700 text-lg mt-2">
                        {{ selectedPatient.esi_explanation }}
                      </p>
                    </div>
                    <div v-else>
                      <label class="block text-sm font-medium text-gray-700 mb-1"
                        >Priority Level</label
                      >
                      <select
                        v-model="editedPatient.priority"
                        class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                      >
                        <option
                          v-for="option in priorityOptions"
                          :key="option.value"
                          :value="option.value"
                        >
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
                      <option
                        v-for="option in statusOptions"
                        :key="option.value"
                        :value="option.value"
                      >
                        {{ option.label }}
                      </option>
                    </select>
                  </div>
                  <div v-else class="mt-2">
                    <span
                      :class="[
                        getStatusColor(selectedPatient.status),
                        'px-3 py-1 rounded-full text-sm font-medium',
                      ]"
                    >
                      {{ getStatusLabel(selectedPatient.status) }}
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
                        <p class="text-lg text-gray-900">
                          {{ formatDate(selectedPatient.dateOfBirth) }}
                        </p>
                      </div>
                      <div>
                        <p class="text-sm text-gray-500">Phone Number</p>
                        <p class="text-lg text-gray-900">{{ selectedPatient.phoneNumber }}</p>
                      </div>
                      <div class="col-span-2">
                        <p class="text-sm text-gray-500">Visit Information</p>
                        <p class="text-lg text-gray-900">
                          {{ formatDate(selectedPatient.dateOfVisit) }} at
                          {{ formatTime(selectedPatient.timeEntered) }}
                        </p>
                      </div>
                    </div>

                    <!-- Edit Mode -->
                    <div v-else class="space-y-4">
                      <div class="grid grid-cols-2 gap-4">
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1"
                            >First Name</label
                          >
                          <input
                            type="text"
                            v-model="editedPatient.firstName"
                            class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                          />
                        </div>
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1"
                            >Last Name</label
                          >
                          <input
                            type="text"
                            v-model="editedPatient.lastName"
                            class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                          />
                        </div>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1"
                            >Date of Birth</label
                          >
                          <input
                            type="date"
                            v-model="editedPatient.dateOfBirth"
                            class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                          />
                        </div>
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1"
                            >Phone Number</label
                          >
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
                          {{
                            selectedPatient.bloodPressure ||
                            selectedPatient.vitals?.bloodPressure ||
                            'N/A'
                          }}
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
                          <label class="block text-sm font-medium text-gray-700 mb-1"
                            >Temperature (°F)</label
                          >
                          <input
                            type="number"
                            v-model="editedPatient.vitals.temperature"
                            class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                          />
                        </div>
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1"
                            >Pulse (bpm)</label
                          >
                          <input
                            type="number"
                            v-model="editedPatient.vitals.pulse"
                            class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                          />
                        </div>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1"
                            >Blood Pressure</label
                          >
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
                          <label class="block text-sm font-medium text-gray-700 mb-1"
                            >Respiration Rate (/min)</label
                          >
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
                    <!-- View Mode -->
                    <div v-if="!isEditing">
                      <div v-if="selectedPatient.allergies?.length" class="flex flex-wrap gap-2">
                        <span
                          v-for="allergy in selectedPatient.allergies"
                          :key="allergy"
                          class="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm"
                        >
                          {{ allergy }}
                        </span>
                      </div>
                      <p v-else class="text-gray-600">No known allergies</p>
                    </div>

                    <!-- Edit Mode -->
                    <div v-else class="space-y-4">
                      <label class="block text-sm font-medium text-gray-700 mb-1"
                        >Select Allergies</label
                      >
                      <div
                        class="bg-white p-4 rounded border border-gray-300 max-h-60 overflow-y-auto"
                      >
                        <div class="grid grid-cols-2 gap-2">
                          <div
                            v-for="option in allergyOptions"
                            :key="option"
                            class="flex items-center"
                          >
                            <input
                              type="checkbox"
                              :id="'allergy-' + option"
                              :value="option"
                              v-model="editedPatient.allergies"
                              class="h-4 w-4 text-blue-600 focus:ring-blue-500 rounded"
                            />
                            <label :for="'allergy-' + option" class="ml-2 text-sm text-gray-700">{{
                              option
                            }}</label>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Substance Use -->
                <div>
                  <h3 class="text-xl font-semibold text-gray-900 mb-4">Substance Use</h3>
                  <div class="bg-gray-50 rounded-lg p-6">
                    <!-- View Mode -->
                    <div v-if="!isEditing">
                      <div
                        v-if="selectedPatient.substance_use?.length"
                        class="flex flex-wrap gap-2"
                      >
                        <span
                          v-for="substance in selectedPatient.substance_use"
                          :key="substance"
                          class="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm"
                        >
                          {{ substance }}
                        </span>
                      </div>
                      <p v-else class="text-gray-600">No substance use reported</p>
                    </div>

                    <!-- Edit Mode -->
                    <div v-else class="space-y-4">
                      <label class="block text-sm font-medium text-gray-700 mb-1"
                        >Select Substance Use</label
                      >
                      <div class="bg-white p-4 rounded border border-gray-300">
                        <div class="space-y-2">
                          <div
                            v-for="option in substanceUseOptions"
                            :key="option"
                            class="flex items-center"
                          >
                            <input
                              type="checkbox"
                              :id="'substance-' + option"
                              :value="option"
                              v-model="editedPatient.substance_use"
                              class="h-4 w-4 text-blue-600 focus:ring-blue-500 rounded"
                            />
                            <label
                              :for="'substance-' + option"
                              class="ml-2 text-sm text-gray-700"
                              >{{ option }}</label
                            >
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Family History -->
                <div>
                  <h3 class="text-xl font-semibold text-gray-900 mb-4">Family History</h3>
                  <div class="bg-gray-50 rounded-lg p-6">
                    <!-- View Mode -->
                    <div v-if="!isEditing">
                      <div
                        v-if="selectedPatient.family_history?.length"
                        class="flex flex-wrap gap-2"
                      >
                        <span
                          v-for="condition in selectedPatient.family_history"
                          :key="condition"
                          class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm"
                        >
                          {{ condition }}
                        </span>
                      </div>
                      <p v-else class="text-gray-600">No family history reported</p>
                    </div>

                    <!-- Edit Mode -->
                    <div v-else class="space-y-4">
                      <label class="block text-sm font-medium text-gray-700 mb-1"
                        >Select Family History</label
                      >
                      <div
                        class="bg-white p-4 rounded border border-gray-300 max-h-60 overflow-y-auto"
                      >
                        <div class="grid grid-cols-2 gap-2">
                          <div
                            v-for="option in familyHistoryOptions"
                            :key="option"
                            class="flex items-center"
                          >
                            <input
                              type="checkbox"
                              :id="'family-' + option"
                              :value="option"
                              v-model="editedPatient.family_history"
                              class="h-4 w-4 text-blue-600 focus:ring-blue-500 rounded"
                            />
                            <label :for="'family-' + option" class="ml-2 text-sm text-gray-700">{{
                              option
                            }}</label>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div v-if="selectedPatient.allergies?.length" class="space-y-2">
                      <div
                        v-for="allergy in selectedPatient.allergies"
                        :key="allergy.name"
                        class="p-2 bg-white rounded"
                      >
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
                          <p class="text-lg text-gray-900 mt-1">
                            {{ selectedPatient.symptoms.notes || 'None' }}
                          </p>
                        </div>
                      </div>
                      <div v-else class="space-y-4">
                        <p class="text-lg text-gray-900">{{ selectedPatient.displaySymptoms }}</p>
                      </div>
                    </div>

                    <!-- Edit Mode -->
                    <div v-else-if="isEditing" class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1"
                          >Select Symptoms</label
                        >
                        <div
                          class="bg-white p-4 rounded border border-gray-300 max-h-60 overflow-y-auto"
                        >
                          <div class="grid grid-cols-2 gap-2">
                            <div
                              v-for="option in symptomOptions"
                              :key="option"
                              class="flex items-center"
                            >
                              <input
                                type="checkbox"
                                :id="'symptom-' + option"
                                :value="option"
                                v-model="editedPatient.symptoms.selected"
                                class="h-4 w-4 text-blue-600 focus:ring-blue-500 rounded"
                              />
                              <label
                                :for="'symptom-' + option"
                                class="ml-2 text-sm text-gray-700"
                                >{{ option }}</label
                              >
                            </div>
                          </div>
                        </div>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1"
                          >Symptoms Description</label
                        >
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
                      <p class="text-lg text-gray-900">
                        {{ selectedPatient.notes || 'No notes available' }}
                      </p>
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
                      <div
                        v-for="medication in selectedPatient.medications"
                        :key="medication.name"
                        class="p-2 bg-white rounded"
                      >
                        <p class="font-medium text-gray-900">{{ medication.name }}</p>
                        <p class="text-sm text-gray-600">
                          {{ medication.dosage }} - {{ medication.frequency }}
                        </p>
                      </div>
                    </div>
                    <p v-else class="text-gray-600">No current medications</p>
                  </div>
                </div>

                <!-- Treatment Plan -->
                <div>
                  <h3 class="text-xl font-semibold text-gray-900 mb-4">Treatment Plan</h3>
                  <div class="bg-gray-50 rounded-lg p-6">
                    <div v-if="!isEditing">
                      <p class="text-lg text-gray-900 whitespace-pre-line">
                        {{ selectedPatient.treatmentPlan || 'No treatment plan available' }}
                      </p>
                    </div>
                    <div v-else>
                      <textarea
                        v-model="editedPatient.treatmentPlan"
                        rows="6"
                        class="px-4 py-2 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full resize-none"
                        placeholder="Enter treatment plan details"
                      ></textarea>
                    </div>
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

  <!-- Emergency Rooms Modal -->
  <Transition name="modal">
    <div
      v-if="showEmergencyRoomsModal"
      class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-[60]"
    >
      <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold text-gray-900">Relocate Patient: Select Hospital</h2>
          <button
            @click="closeRelocateModal"
            class="px-3 py-1 border border-gray-300 rounded text-gray-700 hover:bg-gray-50 transition"
          >
            Cancel
          </button>
        </div>

        <div class="flex-grow flex flex-col md:flex-row gap-4 overflow-hidden">
          <!-- Map Area -->
          <div class="w-full md:w-2/3 h-64 md:h-auto border rounded-lg overflow-hidden">
            <iframe
              width="100%"
              height="100%"
              style="border: 0"
              loading="lazy"
              allowfullscreen
              referrerpolicy="no-referrer-when-downgrade"
              :src="googleMapsEmbedUrl"
            >
            </iframe>
            <p class="text-xs text-gray-500 p-1">
              If map doesn't load, ensure API key is set (check .env file and restart dev server)
              and valid, or that the query is specific enough.
            </p>
          </div>

          <!-- Hospital List Area -->
          <div
            class="w-full md:w-1/3 flex-shrink-0 overflow-y-auto pr-2 space-y-2 md:max-h-[calc(90vh-200px)]"
          >
            <div v-if="loadingEmergencyRooms" class="text-center py-4">
              <p class="text-gray-600">Loading emergency rooms...</p>
            </div>
            <div v-else-if="errorEmergencyRooms" class="text-center py-4 text-red-600">
              <p>{{ errorEmergencyRooms }}</p>
            </div>
            <div v-else-if="emergencyRoomsData.length === 0" class="text-center py-4 text-gray-600">
              <p>No emergency rooms found.</p>
            </div>
            <div
              v-for="(hospital, index) in emergencyRoomsData"
              :key="hospital.place_id || index"
              @click="selectHospitalForRelocation(hospital)"
              :class="[
                'p-3 rounded-lg border cursor-pointer hover:bg-gray-100 transition-colors',
                selectedRelocationHospital === hospital
                  ? 'bg-blue-100 border-blue-400 ring-2 ring-blue-300'
                  : 'bg-gray-50 border-gray-200',
              ]"
            >
              <h3 class="text-md font-semibold text-gray-800">{{ hospital.name }}</h3>
              <p v-if="hospital.vicinity" class="text-sm text-gray-600">{{ hospital.vicinity }}</p>
              <p v-else class="text-sm text-gray-500 italic">Address not available</p>
            </div>
          </div>
        </div>

        <div class="mt-6 flex justify-end items-center">
          <div v-if="selectedRelocationHospital" class="text-sm text-gray-700 mr-4">
            Selected: <span class="font-semibold">{{ selectedRelocationHospital.name }}</span>
          </div>
          <button
            @click="confirmPatientRelocation"
            :disabled="!selectedRelocationHospital || loadingEmergencyRooms"
            class="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center"
          >
            <svg
              v-if="loadingEmergencyRooms"
              class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              ></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Relocate Patient & Remove from List
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
/* Base styles */
.min-h-screen {
  background: linear-gradient(135deg, #f6f8fc 0%, #f1f4f9 100%);
}

/* Card styles */
.draggable-item {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(226, 232, 240, 0.8);
  /* backdrop-filter: blur(8px); removed for solid pastel backgrounds */
  /* background: rgba(255, 255, 255, 0.9); removed to use Tailwind bg classes */
}

.draggable-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 20px -8px rgba(0, 0, 0, 0.1);
  border-color: rgba(226, 232, 240, 1);
}

/* Status badges */
.status-badge {
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.status-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Priority badges */
.priority-badge {
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.priority-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Modal styles */
.modal-content-enter-active,
.modal-content-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-content-enter-from,
.modal-content-leave-to {
  transform: scale(0.95) translateY(-10px);
  opacity: 0;
}

/* Form elements */
textarea {
  resize: vertical;
  transition: all 0.2s ease;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Buttons */
button {
  transition: all 0.2s ease;
}

button:hover {
  transform: translateY(-1px);
}

/* Busyness prediction box */
.bg-blue-50 {
  transition: all 0.3s ease;
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.bg-blue-50:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 12px -2px rgba(0, 0, 0, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
}

/* Notification styles */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.notification-enter-from,
.notification-leave-to {
  transform: translateX(100%) translateY(-10px);
  opacity: 0;
}

/* Header styles */
h2.text-2xl {
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Drag ghost styles */
.draggable-item.sortable-ghost {
  opacity: 0.5;
  background: #f8fafc;
  border: 2px dashed #cbd5e1;
}

.draggable-item.sortable-chosen {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  transform: scale(1.02);
}
</style>
