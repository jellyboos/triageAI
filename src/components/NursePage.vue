<script setup>
const emit = defineEmits(['navigate'])

const goBack = () => {
  emit('navigate', 'landing')
}
</script>

<template>
  <div class="page">
    <button class="back-button" @click="goBack">← Back to Main</button>
    <h2>Nurse Page</h2>
  </div>
</template>

<style scoped>
.page {
  padding: 2rem;
  text-align: center;
}

.back-button {
  background-color: #666;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 1rem;
}
</style>
