<template>
  <header class="navbar">
    <div class="navbar-container">
      <button class="toggle-btn" @click="$emit('toggle-sidebar')" aria-label="Toggle sidebar">
        ☰
      </button>
      <div class="logo">
        <img src="@/assets/logo.svg" alt="Logo" />
      </div>
      <div class="search">
        <input type="text" placeholder="Search..." />
      </div>
      <div class="user-menu" v-if="isAuthenticated">
        <button class="user-btn" @click="toggleDropdown">
          {{ userName }}
        </button>
        <div class="dropdown" v-show="showDropdown">
          <router-link to="/profile" class="dropdown-item">Profile</router-link>
          <router-link to="/logout" class="dropdown-item">Logout</router-link>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/auth/stores/auth.store'

const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)
const userName = computed(() => user.value?.name || 'User')

const showDropdown = ref(false)

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  background-color: var(--color-background);
  border-bottom: 1px solid var(--color-border);
  z-index: 100;
  padding: 1rem 0;
}

.navbar-container {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0 2rem;
}

.toggle-btn {
  display: none;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--color-text);
  cursor: pointer;
  padding: 0.5rem;
}

.logo img {
  height: 40px;
  width: auto;
}

.search {
  flex: 1;
  max-width: 400px;
}

.search input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background-color: var(--color-background-soft);
  color: var(--color-text);
  font-family: inherit;
  font-size: 1rem;
}

.user-menu {
  position: relative;
}

.user-btn {
  background: none;
  border: none;
  color: var(--color-text);
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.user-btn:hover {
  background-color: var(--color-border-hover);
}

.dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  min-width: 150px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.dropdown-item {
  display: block;
  padding: 0.75rem 1rem;
  color: var(--color-text);
  text-decoration: none;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background-color: var(--color-border-hover);
}

@media (max-width: 768px) {
  .toggle-btn {
    display: block;
  }

  .navbar-container {
    padding: 0 1rem;
    gap: 0.5rem;
  }

  .search {
    display: none;
  }

  .user-menu {
    margin-left: auto;
  }
}
</style>