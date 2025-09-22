<template>
  <div class="admin-view">
    <div class="admin-header">
      <h1>Панель администратора</h1>
      <p class="admin-subtitle">Управление системой и пользователями</p>
    </div>

    <div class="admin-content">
      <div class="admin-stats">
        <div class="stat-card">
          <div class="stat-icon">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </div>
          <div class="stat-info">
            <h3>Пользователи</h3>
            <p class="stat-number">1,234</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <rect width="20" height="14" x="2" y="5" rx="2" />
              <path d="M2 10h20" />
            </svg>
          </div>
          <div class="stat-info">
            <h3>Заказы</h3>
            <p class="stat-number">567</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
          </div>
          <div class="stat-info">
            <h3>Доход</h3>
            <p class="stat-number">₽89,432</p>
          </div>
        </div>
      </div>

      <div class="admin-actions">
        <div class="action-card">
          <h3>Управление пользователями</h3>
          <p>Создание, редактирование и удаление учетных записей</p>
          <button class="btn btn-primary">Перейти</button>
        </div>

        <div class="action-card">
          <h3>Системные настройки</h3>
          <p>Настройка параметров системы и безопасности</p>
          <button class="btn btn-secondary">Перейти</button>
        </div>

        <div class="action-card">
          <h3>Мониторинг</h3>
          <p>Отслеживание производительности и логов</p>
          <button class="btn btn-secondary">Перейти</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '../auth'

const authStore = useAuthStore()

/**
 * Проверка прав доступа при монтировании компонента
 */
onMounted(() => {
  if (!authStore.hasRole('admin')) {
    console.warn('Доступ запрещен: недостаточно прав')
  }
})
</script>

<style scoped>
.admin-view {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.admin-header {
  margin-bottom: 3rem;
  text-align: center;
}

.admin-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.admin-subtitle {
  color: #6b7280;
  font-size: 1.125rem;
}

.admin-content {
  display: grid;
  gap: 3rem;
}

.admin-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: #3b82f6;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-info h3 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-number {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.admin-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.action-card:hover {
  transform: translateY(-2px);
}

.action-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.action-card p {
  color: #6b7280;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

@media (max-width: 768px) {
  .admin-view {
    padding: 1rem;
  }

  .admin-header h1 {
    font-size: 2rem;
  }

  .admin-stats {
    grid-template-columns: 1fr;
  }

  .admin-actions {
    grid-template-columns: 1fr;
  }
}
</style>