<template>
  <div class="register-success">
    <div class="success-container">
      <div class="success-icon">
        <svg
          width="64"
          height="64"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
          <polyline points="22,4 12,14.01 9,11.01" />
        </svg>
      </div>

      <h1 class="success-title">Регистрация завершена!</h1>

      <p class="success-message">
        Ваш аккаунт успешно создан. Теперь вы можете войти в систему с помощью
        вашего email и пароля.
      </p>

      <div class="success-actions">
        <button
          @click="goToLogin"
          class="btn btn-primary"
        >
          Войти в систему
        </button>

        <button
          @click="goToHome"
          class="btn btn-secondary"
        >
          На главную
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

/**
 * Переход на страницу входа
 */
const goToLogin = (): void => {
  router.push({ name: 'login' })
}

/**
 * Переход на главную страницу
 */
const goToHome = (): void => {
  router.push({ name: 'home' })
}
</script>

<style scoped>
.register-success {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.success-container {
  background: white;
  border-radius: 1rem;
  padding: 3rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.success-icon {
  color: #10b981;
  margin-bottom: 1.5rem;
}

.success-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.success-message {
  color: #6b7280;
  font-size: 1.125rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.success-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 0.75rem 2rem;
  border-radius: 0.5rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #e5e7eb;
  transform: translateY(-1px);
}

@media (max-width: 640px) {
  .success-container {
    padding: 2rem;
  }

  .success-title {
    font-size: 1.5rem;
  }

  .success-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>