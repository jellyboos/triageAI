<script setup>
const emit = defineEmits(['navigate'])

const navigateTo = (page) => {
  emit('navigate', page)
}
</script>

<template>
  <div class="landing">
    <h1>Emergency Triage System</h1>
    <div class="buttons">
      <button @click="navigateTo('patient')">Patient Check-in</button>
      <button @click="navigateTo('nurse')">Nurse Portal</button>
    </div>
  </div>
</template>

<style scoped>
.landing {
  text-align: center;
  padding: 2rem;
}

.buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

button {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  cursor: pointer;
}
</style>
