<template>
  <div class="unauthorized-view">
    <div class="unauthorized-container">
      <div class="unauthorized-icon">
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
          <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
          <circle cx="12" cy="16" r="1" />
          <path d="M7 11V7a5 5 0 0 1 10 0v4" />
        </svg>
      </div>

      <h1 class="unauthorized-title">Доступ запрещен</h1>

      <p class="unauthorized-message">
        У вас нет прав для доступа к этой странице. Возможно, вам нужно войти в
        систему или у вас недостаточно прав для просмотра этого контента.
      </p>

      <div class="unauthorized-actions">
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

      <div class="unauthorized-help">
        <p>
          Если вы считаете, что это ошибка, пожалуйста,
          <a href="mailto:support@example.com">свяжитесь с поддержкой</a>
        </p>
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
.unauthorized-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.unauthorized-container {
  background: white;
  border-radius: 1rem;
  padding: 3rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.unauthorized-icon {
  color: #f59e0b;
  margin-bottom: 1.5rem;
}

.unauthorized-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.unauthorized-message {
  color: #6b7280;
  font-size: 1.125rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.unauthorized-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 2rem;
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

.unauthorized-help {
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.unauthorized-help p {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

.unauthorized-help a {
  color: #3b82f6;
  text-decoration: none;
}

.unauthorized-help a:hover {
  text-decoration: underline;
}

@media (max-width: 640px) {
  .unauthorized-container {
    padding: 2rem;
  }

  .unauthorized-title {
    font-size: 1.5rem;
  }

  .unauthorized-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>