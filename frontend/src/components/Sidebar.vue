<template>
  <nav class="sidebar">
    <ul class="nav-list">
      <li v-for="item in navItems" :key="item.path" class="nav-item">
        <router-link :to="item.path" class="nav-link" active-class="nav-link-active" exact-active-class="nav-link-exact-active">
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
  { path: '/dashboard', label: 'Главная' },
  { path: '/posts', label: 'Посты' },
  { path: '/authors', label: 'Авторы' },
  { path: '/groups', label: 'Группы' },
  { path: '/profile', label: 'Профиль' }
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

.nav-link-active {
  background-color: var(--color-background-mute);
  color: var(--color-text-accent);
  font-weight: 500;
}

.nav-link-exact-active {
  background-color: var(--color-background-active, var(--color-border-hover));
  color: var(--color-text-active, var(--color-text));
  font-weight: 600;
  border-left: 4px solid var(--color-accent, #007bff);
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