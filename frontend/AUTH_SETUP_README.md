# Настройка системы аутентификации Vue.js

## 📋 Обзор настройки

Эта инструкция поможет вам настроить полнофункциональную систему аутентификации для вашего Vue.js приложения.

## 🚀 Шаги настройки

### 1. Установка зависимостей

Убедитесь, что у вас установлены необходимые пакеты:

```bash
npm install vue vue-router pinia axios
npm install -D typescript @types/node
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе примера:

```bash
cp .env.example .env
```

Основные переменные для настройки:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=10000

# Authentication Configuration
VITE_AUTH_TOKEN_REFRESH_THRESHOLD=300000
VITE_AUTH_AUTO_REFRESH=true
VITE_AUTH_REDIRECT_AFTER_LOGIN=/
VITE_AUTH_REDIRECT_AFTER_LOGOUT=/auth/login

# Application Configuration
VITE_APP_NAME=Vue.js Application
VITE_APP_VERSION=1.0.0
VITE_APP_ENVIRONMENT=development
```

### 3. Инициализация в main.ts

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Импорт системы аутентификации
import { initializeAuth } from './auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Инициализация аутентификации
initializeAuth()

app.mount('#app')
```

### 4. Настройка роутера

Обновите `src/router/index.ts`:

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { authGuard } from '../auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Защищенные роуты
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },

    // Роуты аутентификации
    {
      path: '/auth/login',
      name: 'login',
      component: () => import('../auth/components/LoginForm.vue'),
      meta: { requiresGuest: true }
    }
  ]
})

// Добавьте guard
router.beforeEach(authGuard)

export default router
```

### 5. Использование в компонентах

#### Форма входа

```vue
<template>
  <div>
    <LoginForm @success="handleLoginSuccess" />
  </div>
</template>

<script setup lang="ts">
import { LoginForm } from '../auth'

const handleLoginSuccess = (user: User) => {
  console.log('Вход выполнен:', user)
  // Редирект или другие действия
}
</script>
```

#### Проверка аутентификации

```vue
<template>
  <div v-if="authStore.isAuthenticated">
    Добро пожаловать, {{ authStore.user?.full_name }}!
    <button @click="logout">Выйти</button>
  </div>
  <div v-else>
    <LoginForm />
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '../auth'

const authStore = useAuthStore()

const logout = async () => {
  await authStore.logout()
}
</script>
```

#### Защита роутов

```vue
<script setup lang="ts">
import { useAuthStore } from '../auth'

const authStore = useAuthStore()

// Проверка прав доступа
const canEdit = authStore.hasPermission('edit_posts')
const isAdmin = authStore.hasRole('admin')
</script>
```

## 🔧 Конфигурация API

### Настройка базового URL

```typescript
// В .env
VITE_API_BASE_URL=http://localhost:8000/api
```

### Настройка перехватчиков

Система автоматически настраивает HTTP перехватчики для:
- Добавления токенов авторизации
- Обновления токенов при истечении
- Обработки ошибок аутентификации

### Кастомизация перехватчиков

```typescript
import { authInterceptor } from '../auth/services'

authInterceptor.setup({
  onTokenRefresh: (newToken: string) => {
    console.log('Токен обновлен:', newToken)
  },
  onError: (error: AuthError) => {
    console.error('Ошибка аутентификации:', error)
  }
})
```

## 🛡️ Guards и middleware

### Доступные guards

- `authGuard` - Основная проверка аутентификации
- `guestGuard` - Только для неавторизованных пользователей
- `roleGuard` - Проверка ролей
- `permissionGuard` - Проверка разрешений

### Настройка middleware

```typescript
import { TokenMiddleware } from '../auth/middleware'

const tokenMiddleware = new TokenMiddleware({
  refreshThreshold: 5 * 60 * 1000, // 5 минут
  autoRefresh: true,
  maxRetries: 3
})

tokenMiddleware.start()
```

## 📊 Управление состоянием

### Pinia Store

```typescript
import { useAuthStore } from '../auth/stores'

const authStore = useAuthStore()

// Аутентификация
await authStore.login({
  email: 'user@example.com',
  password: 'password'
})

// Проверка состояния
console.log('Авторизован:', authStore.isAuthenticated)
console.log('Пользователь:', authStore.user)
console.log('Роли:', authStore.userRoles)

// Выход
await authStore.logout()
```

## 🔧 Дополнительные настройки

### Включение отладки

```env
VITE_LOG_LEVEL=debug
VITE_ENABLE_DEVTOOLS=true
VITE_ENABLE_PERFORMANCE_MONITORING=true
```

### Настройка мониторинга

```env
VITE_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
VITE_GOOGLE_ANALYTICS_ID=GA-TRACKING-ID
```

### Социальные сети

```env
VITE_GOOGLE_CLIENT_ID=your-google-client-id
VITE_FACEBOOK_APP_ID=your-facebook-app-id
VITE_GITHUB_CLIENT_ID=your-github-client-id
```

## 🧪 Тестирование

### Запуск тестов

```bash
npm run test
```

### Пример теста

```typescript
import { describe, it, expect } from 'vitest'
import { TokenUtils } from '../auth/utils'

describe('TokenUtils', () => {
  it('should decode valid token', () => {
    const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    const decoded = TokenUtils.decodeToken(token)

    expect(decoded).toBeTruthy()
    expect(decoded.sub).toBe('user123')
  })
})
```

## 🚀 Production настройка

### Оптимизации

```env
VITE_ENABLE_HOT_RELOAD=false
VITE_ENABLE_DEVTOOLS=false
VITE_LOG_LEVEL=error
VITE_ENABLE_SERVICE_WORKER=true
```

### Безопасность

```env
VITE_ENABLE_HTTPS=true
VITE_CORS_ENABLED=false
VITE_ENABLE_TWO_FACTOR_AUTH=true
```

## 📱 Адаптивность

Все компоненты адаптивны и поддерживают:
- Мобильные устройства (320px+)
- Планшеты (768px+)
- Десктоп (1024px+)
- Высокий DPI

## 🌐 Интернационализация

```typescript
import { authConfig } from '../auth/config'

const languages = authConfig.get('supportedLanguages')
const currentLang = authConfig.get('defaultLanguage')
```

## 🔍 Отладка

### Логирование

```typescript
import { authConfig } from '../auth/config'

if (authConfig.isDevelopment()) {
  console.log('Режим разработки включен')
}
```

### Инструменты разработчика

- Vue DevTools для отладки состояния
- Network tab для мониторинга API
- Console для просмотра логов

## 🆘 Решение проблем

### Проверка конфигурации

```typescript
import { authConfig } from '../auth/config'

const validation = authConfig.validateConfig()
if (!validation.isValid) {
  console.error('Ошибки конфигурации:', validation.errors)
}
```

### Проверка токенов

```typescript
import { TokenUtils } from '../auth/utils'

const token = localStorage.getItem('access_token')
if (token) {
  console.log('Токен действителен:', TokenUtils.isTokenValid(token))
  console.log('Время до истечения:', TokenUtils.getTokenExpirationTime(token))
}
```

## 📚 Дополнительная документация

- [API документация](./src/auth/README.md)
- [Архитектура системы](./AUTHENTICATION_ARCHITECTURE.md)
- [Примеры использования](./src/auth/examples/)

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте консоль браузера на ошибки
2. Убедитесь в правильности настройки переменных окружения
3. Проверьте работу API бэкенда
4. Обратитесь к документации

---

**Система аутентификации готова к использованию!** 🎉

После выполнения всех шагов настройки у вас будет полнофункциональная система аутентификации с:
- Автоматическим обновлением токенов
- Защитой роутов
- Управлением состоянием
- Обработкой ошибок
- Адаптивным интерфейсом