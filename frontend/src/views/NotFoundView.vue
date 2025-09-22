<template>
  <div class="not-found-view">
    <div class="not-found-container">
      <div class="not-found-icon">
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
          <circle cx="12" cy="12" r="10" />
          <path d="M16 16s-1.5-2-4-2-4 2-4 2" />
          <line x1="9" y1="9" x2="9.01" y2="9" />
          <line x1="15" y1="9" x2="15.01" y2="9" />
        </svg>
      </div>

      <h1 class="not-found-title">404</h1>

      <h2 class="not-found-subtitle">Страница не найдена</h2>

      <p class="not-found-message">
        К сожалению, страница, которую вы ищете, не существует или была перемещена.
      </p>

      <div class="not-found-actions">
        <button
          @click="goToHome"
          class="btn btn-primary"
        >
          На главную
        </button>

        <button
          @click="goBack"
          class="btn btn-secondary"
        >
          Назад
        </button>
      </div>

      <div class="not-found-help">
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
 * Переход на главную страницу
 */
const goToHome = (): void => {
  router.push({ name: 'home' })
}

/**
 * Возврат на предыдущую страницу
 */
const goBack = (): void => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    goToHome()
  }
}
</script>

<style scoped>
.not-found-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.not-found-container {
  background: white;
  border-radius: 1rem;
  padding: 3rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.not-found-icon {
  color: #6b7280;
  margin-bottom: 1.5rem;
}

.not-found-title {
  font-size: 4rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
  line-height: 1;
}

.not-found-subtitle {
  font-size: 1.5rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
}

.not-found-message {
  color: #6b7280;
  font-size: 1.125rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.not-found-actions {
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

.not-found-help {
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.not-found-help p {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

.not-found-help a {
  color: #3b82f6;
  text-decoration: none;
}

.not-found-help a:hover {
  text-decoration: underline;
}

@media (max-width: 640px) {
  .not-found-container {
    padding: 2rem;
  }

  .not-found-title {
    font-size: 3rem;
  }

  .not-found-subtitle {
    font-size: 1.25rem;
  }

  .not-found-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>