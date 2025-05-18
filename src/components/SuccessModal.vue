<script setup>
import { onMounted } from 'vue'

const emit = defineEmits(['close'])

onMounted(() => {
  setTimeout(() => {
    emit('close')
  }, 2000)
})
</script>

<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <div class="checkmark-circle">
        <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
          <circle class="checkmark-circle-bg" cx="26" cy="26" r="25" fill="none" />
          <path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8" />
        </svg>
      </div>
      <h2 class="text-2xl font-bold text-gray-800 mt-4">Success!</h2>
      <p class="text-gray-600 mt-2">Patient information submitted successfully</p>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  text-align: center;
  animation: slideIn 0.3s ease-out;
}

.checkmark-circle {
  width: 80px;
  height: 80px;
  margin: 0 auto;
}

.checkmark {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: block;
  stroke-width: 2;
  stroke: #4caf50;
  stroke-miterlimit: 10;
  animation: scale 0.3s ease-in-out 0.9s both;
}

.checkmark-circle-bg {
  fill: none;
  stroke: #4caf50;
  stroke-width: 2;
  animation: fill 0.4s ease-in-out 0.4s forwards;
}

.checkmark-check {
  transform-origin: 50% 50%;
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
  stroke: white;
  stroke-width: 3;
}

@keyframes stroke {
  100% {
    stroke-dashoffset: 0;
  }
}

@keyframes scale {
  0%,
  100% {
    transform: none;
  }
  50% {
    transform: scale3d(1.1, 1.1, 1);
  }
}

@keyframes fill {
  100% {
    box-shadow: inset 0px 0px 0px 30px #4caf50;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
