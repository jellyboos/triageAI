<!-- <script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits(['close'])

const hospitalAddress = ref(localStorage.getItem('hospitalAddress') || '')
const addressError = ref(null)

/* global google */
const initGoogleMapsScript = () => {
  const script = document.createElement('script')
  // Replace YOUR_API_KEY with your actual Google Maps API key
  script.src = `https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places`
  script.async = true
  script.defer = true
  document.head.appendChild(script)

  script.onload = () => {
    initAutocomplete()
  }
}

const initAutocomplete = () => {
  const input = document.getElementById('hospitalAddress')
  if (!input) return

  const autocomplete = new google.maps.places.Autocomplete(input, {
    types: ['address'],
    componentRestrictions: { country: 'us' }, // Restrict to US addresses, remove or change as needed
  })

  autocomplete.addListener('place_changed', () => {
    const place = autocomplete.getPlace()
    if (place.formatted_address) {
      hospitalAddress.value = place.formatted_address
    }
  })
}

const saveHospitalAddress = () => {
  try {
    localStorage.setItem('hospitalAddress', hospitalAddress.value)
    addressError.value = null
    emit('close')
  } catch (error) {
    console.error('Failed to save hospital address:', error)
    addressError.value = 'Failed to save hospital address'
  }
}

onMounted(() => {
  initGoogleMapsScript()
})
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50"
  >
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
      <div class="flex justify-between items-start mb-6">
        <h3 class="text-2xl font-bold text-gray-900">Settings</h3>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-500">
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

      <div class="space-y-4">
        <div>
          <label for="hospitalAddress" class="block text-sm font-medium text-gray-700 mb-2">
            Hospital Address
          </label>
          <input
            id="hospitalAddress"
            v-model="hospitalAddress"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Start typing to search address..."
          />
          <p class="mt-1 text-sm text-gray-500">Start typing to see address suggestions</p>
          <p v-if="addressError" class="mt-2 text-sm text-red-600">{{ addressError }}</p>
        </div>

        <div class="flex justify-end">
          <button
            @click="saveHospitalAddress"
            class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
</style> -->
