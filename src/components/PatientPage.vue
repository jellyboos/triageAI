<script setup>
import { ref, onMounted } from 'vue'

const emit = defineEmits(['navigate'])
const message = ref('')
const inputData = ref('')

const goBack = () => {
  emit('navigate', 'landing')
}

const fetchData = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/data')
    const data = await response.json()
    message.value = data.message
  } catch (error) {
    console.error('Error:', error)
  }
}

const sendData = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: inputData.value }),
    })
    const data = await response.json()
    message.value = `Received: ${JSON.stringify(data)}`
  } catch (error) {
    console.error('Error:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="page">
    <button class="back-button" @click="goBack">← Back to Main</button>
    <h2>Patient Page</h2>

    <div class="data-section">
      <p>Message from server: {{ message }}</p>

      <div class="input-group">
        <input v-model="inputData" placeholder="Enter some text" />
        <button @click="sendData">Send to Server</button>
      </div>
    </div>
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

.data-section {
  margin-top: 2rem;
}

.input-group {
  margin-top: 1rem;
}

input {
  padding: 0.5rem;
  margin-right: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  background-color: #4caf50;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
