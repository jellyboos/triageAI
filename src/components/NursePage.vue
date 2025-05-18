<script setup>
import { ref } from 'vue'
import SettingsModal from './SettingsModal.vue'
import draggable from 'vuedraggable'

// Emit events to parent component for navigation
const emit = defineEmits(['navigate'])

// Navigation handler to return to landing page
const goBack = () => {
  emit('navigate', 'landing')
}

// Settings modal state
const showSettings = ref(false)

// Track drag state
const drag = ref(false)

// Track edit state
const isEditing = ref(false)
const editedSymptoms = ref('')
const editedNotes = ref('')
const editedStatus = ref('')
const editedPriority = ref(1)

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
  {
    id: 4,
    name: 'Sarah Williams',
    checkInTime: '2024-03-20T11:15:00',
    status: 'completed',
    priority: 4,
    symptoms: 'Fever, Cough',
    notes: 'Patient reports high fever for 2 days',
  },
  {
    id: 5,
    name: 'David Brown',
    checkInTime: '2024-03-20T11:30:00',
    status: 'completed',
    priority: 5,
    symptoms: 'Fever, Cough',
    notes: 'Patient reports high fever for 2 days',
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

// Start editing patient details
const startEditing = (patient) => {
  isEditing.value = true
  editedSymptoms.value = patient.symptoms
  editedNotes.value = patient.notes
  editedStatus.value = patient.status
  editedPriority.value = patient.priority
}

// Save edited patient details
const saveEdits = () => {
  if (selectedPatient.value) {
    selectedPatient.value.symptoms = editedSymptoms.value
    selectedPatient.value.notes = editedNotes.value
    selectedPatient.value.status = editedStatus.value
    selectedPatient.value.priority = editedPriority.value
    isEditing.value = false
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

// Show notification
const showPriorityChangeNotification = (patient, oldPriority, newPriority) => {
  notificationMessage.value = `Change ${patient.name}'s priority from ${oldPriority} to ${newPriority}?`
  showNotification.value = true
  pendingPriorityChange.value = { patient, newPriority }
}

// Handle drag end and update priority
const handleDragEnd = (evt) => {
  drag.value = false
  if (evt.oldIndex !== evt.newIndex) {
    const movedPatient = patients.value[evt.newIndex]
    const oldPriority = movedPatient.priority
    const newPriority = evt.newIndex + 1 // Priority is 1-based index

    if (oldPriority !== newPriority) {
      showPriorityChangeNotification(movedPatient, oldPriority, newPriority)
    }
  }
}

// Handle notification response
const handleNotificationResponse = (confirmed) => {
  if (confirmed && pendingPriorityChange.value) {
    const { patient, newPriority } = pendingPriorityChange.value
    patient.priority = newPriority
    // Resort the list
    patients.value.sort((a, b) => a.priority - b.priority)
  } else {
    // Revert the drag
    const index = patients.value.findIndex((p) => p.id === pendingPriorityChange.value.patient.id)
    if (index !== -1) {
      const temp = patients.value[index]
      patients.value[index] = patients.value[pendingPriorityChange.value.newPriority - 1]
      patients.value[pendingPriorityChange.value.newPriority - 1] = temp
      // Resort the list
      patients.value.sort((a, b) => a.priority - b.priority)
    }
  }
  showNotification.value = false
  pendingPriorityChange.value = null
}
</script>

<template>
  <!-- Main container - takes full viewport height -->
  <div class="min-h-screen min-w-screen relative">
    <!-- Notification Box -->
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

    <!-- Content wrapper with max width and padding -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header section with back button, title, and settings -->
      <div class="flex justify-between items-center mb-8">
        <button
          @click="goBack"
          class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          ← Back to Main
        </button>
        <h2 class="text-2xl font-bold text-gray-900">Patient Management</h2>
        <button
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
        </button>
      </div>
      <!-- Patient cards container -->
      <div class="flex flex-wrap gap-4 flex-col justify-center items-center">
        <draggable
          :list="patients"
          item-key="id"
          class="w-full"
          @start="drag = true"
          @end="handleDragEnd"
        >
          <template #item="{ element }">
            <div
              @click="openPatientDetail(element)"
              class="bg-white rounded-lg shadow p-4 cursor-move hover:shadow-md transition-shadow flex-1 min-w-[40em] min-h-[10em] mb-4"
            >
              <!-- Card header with name and status -->
              <div class="flex justify-between items-start">
                <div>
                  <h3 class="text-lg font-semibold text-gray-900">{{ element.name }}</h3>
                  <p class="text-sm text-gray-500">
                    Check-in: {{ new Date(element.checkInTime).toLocaleTimeString() }}
                  </p>
                </div>

                <!-- Status badge -->
                <span
                  :class="[
                    getStatusColor(element.status),
                    'px-2 py-1 rounded-full text-xs font-medium',
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
                    'px-2 py-1 rounded-full text-xs font-medium',
                  ]"
                >
                  Priority {{ element.priority }}
                </span>
              </div>
              <!-- Symptoms preview -->
              <p class="mt-2 text-sm text-gray-600">{{ element.symptoms }}</p>
            </div>
          </template>
        </draggable>
      </div>

      <!-- Patient Detail Modal -->
      <div
        v-if="selectedPatient"
        class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50"
      >
        <!-- Modal content -->
        <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full p-8">
          <!-- Modal header with close button -->
          <div class="flex justify-between items-start mb-8">
            <div class="flex items-center gap-6">
              <div>
                <h3 class="text-3xl font-bold text-gray-900">{{ selectedPatient.name }}</h3>
                <p class="text-lg text-gray-500 mt-1">
                  Check-in: {{ new Date(selectedPatient.checkInTime).toLocaleString() }}
                </p>
              </div>
              <div class="flex gap-3">
                <span
                  v-if="!isEditing"
                  :class="[
                    getStatusColor(selectedPatient.status),
                    'px-4 py-2 rounded-full text-base font-medium whitespace-nowrap',
                  ]"
                >
                  {{ selectedPatient.status }}
                </span>
                <select
                  v-else
                  v-model="editedStatus"
                  class="px-4 py-2 rounded-full text-base font-medium border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option v-for="option in statusOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
                <span
                  v-if="!isEditing"
                  :class="[
                    getPriorityColor(selectedPatient.priority),
                    'px-4 py-2 rounded-full text-base font-medium whitespace-nowrap',
                  ]"
                >
                  Priority {{ selectedPatient.priority }}
                </span>
                <select
                  v-else
                  v-model="editedPriority"
                  class="px-4 py-2 rounded-full text-base font-medium border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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
            <div class="flex gap-2">
              <button
                v-if="!isEditing"
                @click="startEditing(selectedPatient)"
                class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Edit
              </button>
              <button @click="closePatientDetail" class="text-gray-400 hover:text-gray-500">
                <span class="sr-only">Close</span>
                <svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          </div>

          <!-- Modal body with patient details -->
          <div class="grid grid-cols-1 gap-8">
            <!-- Symptoms -->
            <div>
              <div class="flex justify-between items-center mb-2">
                <h4 class="text-xl font-medium text-gray-700">Symptoms</h4>
              </div>
              <div v-if="!isEditing" class="text-lg text-gray-900 bg-gray-50 p-4 rounded-lg">
                {{ selectedPatient.symptoms }}
              </div>
              <textarea
                v-else
                v-model="editedSymptoms"
                class="w-full text-lg text-gray-900 bg-gray-50 p-4 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                rows="3"
              ></textarea>
            </div>

            <!-- Notes -->
            <div>
              <h4 class="text-xl font-medium text-gray-700 mb-2">Notes</h4>
              <div v-if="!isEditing" class="text-lg text-gray-900 bg-gray-50 p-4 rounded-lg">
                {{ selectedPatient.notes }}
              </div>
              <textarea
                v-else
                v-model="editedNotes"
                class="w-full text-lg text-gray-900 bg-gray-50 p-4 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                rows="5"
              ></textarea>
            </div>

            <!-- Edit action buttons -->
            <div v-if="isEditing" class="flex justify-end gap-3 mt-4">
              <button
                @click="cancelEditing"
                class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                @click="saveEdits"
                class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Settings Modal -->
      <SettingsModal :show="showSettings" @close="showSettings = false" />
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

.settings-icon {
  transition: transform 0.2s ease;
}

.settings-icon:hover {
  transform: rotate(45deg);
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
