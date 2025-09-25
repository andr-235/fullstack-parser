<template>
  <v-navigation-drawer
    v-model="drawer"
    app
    permanent
    width="280"
    class="sidebar"
  >
    <!-- Header -->
    <div class="sidebar__header pa-4">
      <div class="d-flex align-center">
        <v-icon class="mr-3" size="large" color="primary">mdi-chart-line</v-icon>
        <div>
          <h3 class="text-h6 font-weight-bold">Анализатор VK</h3>
          <p class="text-caption text-medium-emphasis">Комментарии</p>
        </div>
      </div>
    </div>

    <v-divider></v-divider>

    <!-- Navigation Menu -->
    <v-list nav class="sidebar__menu">
      <v-list-item
        v-for="item in menuItems"
        :key="item.to"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="item.title"
        :subtitle="item.subtitle"
        :active="isActiveRoute(item.to)"
        class="sidebar__menu-item"
        rounded="xl"
      >
        <template v-slot:prepend>
          <v-icon :color="isActiveRoute(item.to) ? 'primary' : 'default'">
            {{ item.icon }}
          </v-icon>
        </template>
      </v-list-item>
    </v-list>

    <v-spacer></v-spacer>

    <!-- Footer -->
    <div class="sidebar__footer pa-4">
      <v-divider class="mb-3"></v-divider>

      <!-- Quick Stats -->
      <div class="sidebar__stats">
        <div class="d-flex justify-space-between align-center mb-2">
          <span class="text-caption">Активных задач:</span>
          <v-chip size="small" color="success">{{ activeTasksCount }}</v-chip>
        </div>
        <div class="d-flex justify-space-between align-center">
          <span class="text-caption">Обработано:</span>
          <v-chip size="small" color="info">{{ processedCommentsCount }}</v-chip>
        </div>
      </div>

      <!-- User Info -->
      <div class="sidebar__user mt-4">
        <v-list-item class="px-0">
          <template v-slot:prepend>
            <v-avatar size="32" color="primary">
              <v-icon color="white">mdi-account</v-icon>
            </v-avatar>
          </template>
          <v-list-item-title class="text-caption">Пользователь</v-list-item-title>
          <div class="text-caption text-medium-emphasis">Аналитик</div>
        </v-list-item>
      </div>
    </div>
  </v-navigation-drawer>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useTasksStore } from '@/stores/tasks.js'

/**
 * Компонент боковой панели (AppSidebar)
 * Содержит навигационное меню, статистику и информацию о пользователе
 */

const route = useRoute()
const tasksStore = useTasksStore()

// Постоянно открытый sidebar для desktop
const drawer = ref(true)

// Элементы меню
const menuItems = computed(() => [
  {
    title: 'Задачи',
    subtitle: 'Управление задачами',
    to: '/tasks',
    icon: 'mdi-format-list-bulleted'
  },
  {
    title: 'Группы VK',
    subtitle: 'Управление группами',
    to: '/groups',
    icon: 'mdi-account-group'
  },
  {
    title: 'Старые задачи',
    subtitle: 'Создание задач (legacy)',
    to: '/fetch',
    icon: 'mdi-plus-box'
  },
  {
    title: 'Комментарии',
    subtitle: 'Просмотр результатов',
    to: '/comments',
    icon: 'mdi-comment-multiple'
  }
])

// Статистика (заглушки - в реальном приложении получать из store)
const activeTasksCount = computed(() => tasksStore.taskId ? 1 : 0)
const processedCommentsCount = computed(() => 0) // TODO: Получать из store

/**
 * Проверяет, является ли маршрут активным
 * @param {string} routePath - Путь маршрута
 * @returns {boolean} - true если маршрут активен
 */
const isActiveRoute = (routePath) => {
  // Для "Задачи" - активен на всех страницах задач
  if (routePath === '/tasks') {
    return route.path.startsWith('/tasks')
  }
  // Для "Группы VK" - активен на всех страницах групп
  if (routePath === '/groups') {
    return route.path.startsWith('/groups')
  }
  // Для "Старые задачи" - активен только на /fetch
  if (routePath === '/fetch') {
    return route.path === '/fetch'
  }
  // Для "Комментарии" - активен только на /comments
  if (routePath === '/comments') {
    return route.path === '/comments'
  }
  return false
}
</script>

<style scoped>
.sidebar {
  background: linear-gradient(180deg, #fafafa 0%, #f5f5f5 100%);
  border-right: 1px solid rgba(0, 0, 0, 0.12);
}

.sidebar__header {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  color: white;
  margin: -1px -1px 0 -1px;
}

.sidebar__menu {
  padding: 8px;
}

.sidebar__menu-item {
  margin-bottom: 4px;
  transition: all 0.3s ease;
}

.sidebar__menu-item:hover {
  background-color: rgba(25, 118, 210, 0.08);
  transform: translateX(4px);
}

.sidebar__menu-item.v-list-item--active {
  background: linear-gradient(135deg, rgba(25, 118, 210, 0.1) 0%, rgba(25, 118, 210, 0.05) 100%);
  border-left: 3px solid #1976d2;
}

.sidebar__stats {
  background: rgba(25, 118, 210, 0.05);
  border-radius: 8px;
  padding: 12px;
}

.sidebar__user {
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  padding: 8px;
}

/* Анимации */
.v-list-item {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>