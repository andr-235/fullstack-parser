<template>
  <div id="app">
    <Navbar @toggle-sidebar="toggleSidebar" />
    <Sidebar :class="{ 'open': showSidebar }" />
    <div v-if="showSidebar" class="overlay" @click="toggleSidebar"></div>
    <main class="main-content" :class="{ 'sidebar-open': showSidebar }">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Navbar from './components/Navbar.vue'
import Sidebar from './components/Sidebar.vue'

const showSidebar = ref(false)

const toggleSidebar = () => {
  showSidebar.value = !showSidebar.value
}
</script>

<style>
#app {
  font-family: Inter, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--color-text);
}

.main-content {
  margin-left: 250px;
  margin-top: 70px;
  padding: 2rem;
  transition: margin-left 0.3s ease;
  min-height: calc(100vh - 70px);
}

.sidebar-open .main-content {
  margin-left: 0;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 99;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    padding: 1rem;
  }

  .sidebar-open .main-content {
    margin-left: 0;
  }
}

.overlay {
  display: none;
}

@media (max-width: 768px) {
  .overlay {
    display: block;
  }
}
</style>