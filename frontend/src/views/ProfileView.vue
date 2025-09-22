<template>
  <div class="profile-view">
    <div class="profile-header">
      <div class="profile-avatar">
        <div class="avatar-placeholder">
          {{ userInitials }}
        </div>
      </div>
      <div class="profile-info">
        <h1>{{ user?.fullName || 'Пользователь' }}</h1>
        <p class="profile-email">{{ user?.email }}</p>
        <div class="profile-role">
          <span class="role-badge" :class="userRoleClass">
            {{ userRoleText }}
          </span>
        </div>
      </div>
    </div>

    <div class="profile-content">
      <div class="profile-section">
        <h2>Информация об аккаунте</h2>
        <div class="info-grid">
          <div class="info-item">
            <label>Полное имя</label>
            <p>{{ user?.fullName || 'Не указано' }}</p>
          </div>
          <div class="info-item">
            <label>Email</label>
            <p>{{ user?.email }}</p>
          </div>
          <div class="info-item">
            <label>Дата регистрации</label>
            <p>{{ formatDate(user?.created_at) }}</p>
          </div>
          <div class="info-item">
            <label>Последний вход</label>
            <p>{{ formatDate(user?.last_login) }}</p>
          </div>
        </div>
      </div>

      <div class="profile-section">
        <h2>Безопасность</h2>
        <div class="security-actions">
          <button
            @click="showChangePassword = true"
            class="btn btn-primary"
          >
            Изменить пароль
          </button>
          <button
            @click="handleLogout"
            class="btn btn-secondary"
          >
            Выйти из системы
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно смены пароля -->
    <div v-if="showChangePassword" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Изменить пароль</h3>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <ChangePasswordForm
            @success="handlePasswordChangeSuccess"
            @cancel="closeModal"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../auth'
import ChangePasswordForm from '../auth/components/ChangePasswordForm.vue'

const router = useRouter()
const authStore = useAuthStore()

const showChangePassword = ref(false)

/**
 * Текущий пользователь
 */
const user = computed(() => authStore.user)

/**
 * Инициалы пользователя для аватара
 */
const userInitials = computed(() => {
  if (!user.value?.fullName) return 'U'
  return user.value.fullName
    .split(' ')
    .map((name: string) => name.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

/**
 * Класс для роли пользователя
 */
const userRoleClass = computed(() => {
  const role = user.value?.role
  if (role === 'admin') return 'role-admin'
  if (role === 'moderator') return 'role-moderator'
  return 'role-user'
})

/**
 * Текст роли пользователя
 */
const userRoleText = computed(() => {
  const role = user.value?.role
  if (role === 'admin') return 'Администратор'
  if (role === 'moderator') return 'Модератор'
  return 'Пользователь'
})

/**
 * Форматирование даты
 */
const formatDate = (dateString?: string): string => {
  if (!dateString) return 'Никогда'
  return new Date(dateString).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Обработка выхода из системы
 */
const handleLogout = async (): Promise<void> => {
  try {
    await authStore.logout()
    router.push({ name: 'login' })
  } catch (error) {
    console.error('Ошибка при выходе:', error)
  }
}

/**
 * Обработка успешной смены пароля
 */
const handlePasswordChangeSuccess = (): void => {
  showChangePassword.value = false
  // Показать уведомление об успехе
  console.log('Пароль успешно изменен')
}

/**
 * Закрытие модального окна
 */
const closeModal = (): void => {
  showChangePassword.value = false
}

/**
 * Загрузка данных пользователя
 */
onMounted(async () => {
  if (authStore.isAuthenticated) {
    try {
      await authStore.getCurrentUser()
    } catch (error) {
      console.error('Ошибка при загрузке данных пользователя:', error)
    }
  }
})
</script>

<style scoped>
.profile-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 3rem;
  padding: 2rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.profile-avatar {
  flex-shrink: 0;
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
}

.profile-info h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.profile-email {
  color: #6b7280;
  font-size: 1.125rem;
  margin-bottom: 1rem;
}

.role-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.role-admin {
  background: #dc2626;
  color: white;
}

.role-moderator {
  background: #f59e0b;
  color: white;
}

.role-user {
  background: #10b981;
  color: white;
}

.profile-content {
  display: grid;
  gap: 2rem;
}

.profile-section {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.profile-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.info-grid {
  display: grid;
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item label {
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.info-item p {
  color: #6b7280;
  margin: 0;
}

.security-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 1rem;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  transition: background-color 0.2s ease;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

@media (max-width: 640px) {
  .profile-view {
    padding: 1rem;
  }

  .profile-header {
    flex-direction: column;
    text-align: center;
    padding: 1.5rem;
  }

  .profile-info h1 {
    font-size: 1.5rem;
  }

  .security-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>