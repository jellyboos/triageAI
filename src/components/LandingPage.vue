<script setup>
const emit = defineEmits(['navigate'])

const navigateTo = (page) => {
  emit('navigate', page)
}
</script>

<template>

<!-- nav bar & nurse sign in-->
  <nav class="navbar">
    <div class="navbar-left">
      <h1 class="title">Emergency Triage System</h1>
    </div>
    <div class="navbar-right">
      <button @click="navigateTo('nurse')">Nurse Portal</button>
    </div>
  </nav>

<!-- form button -->
   <div class="landing">
    <div class="button-patient">
      <button @click="navigateTo('patient')">Patient Check-in</button>
    </div>
  </div>
</template>


<style scoped>
/* full page login */
.landing {
  text-align: left;
  padding: 2rem;
  font-size: 1.5rem;
  font-family:Arial, Helvetica, sans-serif
}

/* nav test bar */
.navbar {
  margin-top: 2%;
  overflow: hidden;
  padding-left: 5%;
  padding-right: 5%;
  display: flex;
  justify-content: space-between;
  font-size: 20px;
  /* border: red 2px solid; */
}

.navbar a {
    float: left;
    color: black;
    display: flex;
    flex-direction: row-reverse;
    text-align: left;
    margin-right: 50px;
    text-decoration: none;
    font-size: 20px;
    /* position: fixed; */
  }

/* title */
.title {
  font-weight: bold;
  /* padding-left: 0.5rem; */
  color: #4E5FCC;
  /* margin-top: 1rem; */
  font-size: 1.75rem;
}

 /* nurse sign in button */
.button-nurse {
  display: flex;
  gap: 1rem;
  justify-content: right;
  margin-top: 2rem;
}

/* patient check in button */
.button-patient {
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
