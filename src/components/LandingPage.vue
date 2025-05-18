<script setup>
const emit = defineEmits(['navigate'])

const navigateTo = (page) => {
  emit('navigate', page)
}

const esiLevels = [
  {
    level: 1,
    title: 'Resuscitation',
    description: 'Immediate, life-saving intervention required',
    color: 'bg-red-600',
  },
  {
    level: 2,
    title: 'Emergent',
    description: 'Immediate nursing assessment and rapid treatment',
    color: 'bg-orange-500',
  },
  {
    level: 3,
    title: 'Urgent',
    description: 'Quick attention needed, can wait up to 30 minutes',
    color: 'bg-yellow-500',
  },
  {
    level: 4,
    title: 'Less Urgent',
    description: 'Can wait longer for assessment',
    color: 'bg-blue-500',
  },
  {
    level: 5,
    title: 'Non-urgent',
    description: 'Can wait for routine care',
    color: 'bg-green-500',
  },
]
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <!-- Navbar -->
    <nav class="fixed w-full bg-white/80 backdrop-blur-sm shadow-sm z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex-shrink-0">
            <h1
              class="text-3xl font-bold text-indigo-600 transition-all duration-300 hover:text-indigo-700"
            >
              Automated Triage System
            </h1>
          </div>
          <div>
            <button
              @click="navigateTo('nurse')"
              class="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transform hover:scale-105 transition-all duration-300 shadow-md hover:shadow-lg"
            >
              Nurse Portal
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="pt-24 px-4 sm:px-6 lg:px-8">
      <div class="max-w-7xl mx-auto">
        <!-- Mission Statement -->
        <div class="text-center mb-16 animate-fade-in">
          <h2 class="text-4xl font-bold text-gray-800 mb-4">Revolutionizing Emergency Care</h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Transforming the traditional ER process with AI-powered triage. Walk in → AI assessment
            → Nurse verification → Faster, smarter care.
          </p>
          <!-- CTA Button -->
          <div class="flex justify-center items-center mt-8 text-center">
            <button
              @click="navigateTo('patient')"
              class="group relative px-8 py-4 bg-white text-indigo-600 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 text-center"
            >
              <span class="relative z-10 text-2xl font-semibold text-center">Patient Check-in</span>
              <!-- <div
                class="absolute inset-0 bg-indigo-600 rounded-xl transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-300"
              ></div> -->
              <span
                class="relative z-10 text-2xl font-semibold text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                >Patient Check-in</span
              >
            </button>
          </div>
        </div>

        <!-- ESI Levels -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-16">
          <div
            v-for="level in esiLevels"
            :key="level.level"
            class="transform hover:scale-105 transition-all duration-300"
          >
            <div :class="[level.color, 'rounded-t-lg p-4 text-white']">
              <h3 class="text-2xl font-bold">Level {{ level.level }}</h3>
              <p class="text-lg font-semibold">{{ level.title }}</p>
            </div>
            <div class="bg-white p-4 rounded-b-lg shadow-lg">
              <p class="text-lg text-gray-600">{{ level.description }}</p>
            </div>
          </div>
        </div>

        <!-- Features Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8 mb-16">
          <div
            class="bg-white p-6 rounded-xl shadow-lg transform hover:scale-105 transition-all duration-300"
          >
            <h3 class="text-2xl font-bold text-indigo-600 mb-3">AI-Powered Triage</h3>
            <p class="text-lg text-gray-600">
              Advanced text analysis and image processing for accurate severity assessment
            </p>
          </div>
          <div
            class="bg-white p-6 rounded-xl shadow-lg transform hover:scale-105 transition-all duration-300"
          >
            <h3 class="text-2xl font-bold text-indigo-600 mb-3">Smart Queue Management</h3>
            <p class="text-lg text-gray-600">
              Real-time queue optimization with priority re-evaluation
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 1s ease-in;
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
</style>
