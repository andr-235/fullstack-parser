<template>
  <nav class="sidebar">
    <ul class="nav-list">
      <li v-for="item in navItems" :key="item.path" class="nav-item">
        <router-link :to="item.path" class="nav-link">
          {{ item.label }}
        </router-link>
      </li>
      <li v-if="isAuthenticated" class="nav-item">
        <router-link to="/logout" class="nav-link">
          Logout
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/auth/stores/auth.store'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

const navItems = [
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/posts', label: 'Posts' },
  { path: '/authors', label: 'Authors' },
  { path: '/groups', label: 'Groups' },
  { path: '/profile', label: 'Profile' }
]
</script>

<style scoped>
.sidebar {
  width: 250px;
  background-color: var(--color-background-soft);
  border-right: 1px solid var(--color-border);
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  overflow-y: auto;
  transition: transform 0.3s ease;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin: 0;
}

.nav-link {
  display: block;
  padding: 1rem;
  color: var(--color-text);
  text-decoration: none;
  border-bottom: 1px solid var(--color-border);
}

.nav-link:hover {
  background-color: var(--color-border-hover);
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
  }

  .sidebar.open {
    transform: translateX(0);
  }
}
</style>