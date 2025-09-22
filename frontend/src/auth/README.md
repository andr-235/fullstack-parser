# Система аутентификации Vue.js

Полнофункциональная система аутентификации для Vue.js приложений с поддержкой TypeScript, Pinia и Vue Router.

## 🚀 Быстрый старт

### 1. Установка зависимостей

Убедитесь, что в вашем проекте установлены необходимые зависимости:

```bash
npm install vue vue-router pinia axios
npm install -D typescript @types/node
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Заполните необходимые переменные:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=10000

# Authentication Configuration
VITE_AUTH_TOKEN_REFRESH_THRESHOLD=300000
VITE_AUTH_AUTO_REFRESH=true
VITE_AUTH_REDIRECT_AFTER_LOGIN=/
VITE_AUTH_REDIRECT_AFTER_LOGOUT=/auth/login
```

### 3. Инициализация в main.ts

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Импорт и инициализация системы аутентификации
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

В файле `router/index.ts` добавьте guards и роуты аутентификации:

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

// Добавьте глобальный guard
router.beforeEach(authGuard)

export default router
```

## 📁 Структура файлов

```
src/auth/
├── components/          # Vue компоненты
│   ├── LoginForm.vue
│   ├── RegisterForm.vue
│   ├── ChangePasswordForm.vue
│   └── RegisterSuccess.vue
├── config/             # Конфигурация
│   ├── auth.config.ts
│   ├── constants.ts
│   └── index.ts
├── guards/             # Guards для роутов
│   ├── auth.guards.ts
│   └── index.ts
├── middleware/         # Middleware
│   ├── token.middleware.ts
│   └── index.ts
├── services/           # API сервисы
│   ├── auth.service.ts
│   ├── auth.interceptors.ts
│   └── index.ts
├── stores/             # Pinia stores
│   ├── auth.store.ts
│   └── index.ts
├── types/              # TypeScript типы
│   ├── auth.types.ts
│   ├── api.types.ts
│   └── index.ts
├── utils/              # Утилиты
│   ├── token.utils.ts
│   ├── error.handler.ts
│   └── index.ts
├── index.ts            # Главный экспорт
└── README.md
```

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `VITE_API_BASE_URL` | Базовый URL API | `http://localhost:8000/api` |
| `VITE_API_TIMEOUT` | Таймаут API запросов (мс) | `10000` |
| `VITE_AUTH_TOKEN_REFRESH_THRESHOLD` | Порог обновления токена (мс) | `300000` |
| `VITE_AUTH_AUTO_REFRESH` | Автоматическое обновление токенов | `true` |
| `VITE_AUTH_REDIRECT_AFTER_LOGIN` | Редирект после входа | `/` |
| `VITE_AUTH_REDIRECT_AFTER_LOGOUT` | Редирект после выхода | `/auth/login` |

### Использование конфигурации

```typescript
import { authConfig } from './auth/config'

// Получение конфигурации
const config = authConfig.getConfig()

// Проверка функциональности
if (authConfig.isFeatureEnabled('enableRegistration')) {
  // Регистрация включена
}

// Получение API URL
const apiUrl = authConfig.getApiUrl('auth/login')
```

## 🛡️ Guards и защита роутов

### Метаданные роутов

```typescript
{
  path: '/admin',
  name: 'admin',
  component: AdminView,
  meta: {
    requiresAuth: true,           // Требует аутентификации
    requiresGuest: false,         // Только для гостей
    requiredRoles: ['admin'],     // Требуемые роли
    requiredPermissions: ['manage_users'] // Требуемые разрешения
  }
}
```

### Доступные guards

- `authGuard` - Основной guard для аутентификации
- `guestGuard` - Guard для гостевых страниц
- `roleGuard` - Guard для проверки ролей
- `permissionGuard` - Guard для проверки разрешений

## 🔄 Middleware

### Token Middleware

Автоматически обновляет токены перед истечением:

```typescript
import { TokenMiddleware } from './auth/middleware'

// Создание middleware
const tokenMiddleware = new TokenMiddleware({
  refreshThreshold: 5 * 60 * 1000, // 5 минут
  autoRefresh: true
})

// Запуск middleware
tokenMiddleware.start()
```

## 📊 Управление состоянием

### Pinia Store

```typescript
import { useAuthStore } from './auth/stores'

// Использование в компоненте
const authStore = useAuthStore()

// Аутентификация
await authStore.login({
  email: 'user@example.com',
  password: 'password'
})

// Проверка состояния
if (authStore.isAuthenticated) {
  console.log('Пользователь:', authStore.user)
}

// Выход
await authStore.logout()
```

## 🔐 API Сервисы

### AuthService

```typescript
import { AuthService } from './auth/services'

// Вход в систему
const response = await AuthService.login({
  email: 'user@example.com',
  password: 'password'
})

// Регистрация
const user = await AuthService.register({
  email: 'user@example.com',
  password: 'password',
  full_name: 'John Doe'
})

// Обновление токена
const tokens = await AuthService.refreshToken()

// Смена пароля
await AuthService.changePassword({
  current_password: 'oldpass',
  new_password: 'newpass'
})
```

## 🧩 Компоненты

### LoginForm

```vue
<template>
  <LoginForm
    @success="handleLoginSuccess"
    @error="handleLoginError"
  />
</template>

<script setup lang="ts">
import { LoginForm } from './auth/components'

const handleLoginSuccess = (user: User) => {
  console.log('Вход выполнен:', user)
}

const handleLoginError = (error: AuthError) => {
  console.error('Ошибка входа:', error)
}
</script>
```

### RegisterForm

```vue
<template>
  <RegisterForm
    :show-success-page="true"
    @success="handleRegisterSuccess"
    @error="handleRegisterError"
  />
</template>
```

## 🛠️ Утилиты

### TokenUtils

```typescript
import { TokenUtils } from './auth/utils'

// Декодирование токена
const tokenData = TokenUtils.decodeToken(accessToken)

// Проверка срока действия
const isValid = TokenUtils.isTokenValid(accessToken, 5) // 5 минут

// Получение данных из токена
const email = TokenUtils.getEmailFromToken(accessToken)
const roles = TokenUtils.getRolesFromToken(accessToken)
const userId = TokenUtils.getUserIdFromToken(accessToken)
```

### AuthUtils

```typescript
import { AuthUtils } from './auth/utils'

// Проверка прав доступа
const hasPermission = AuthUtils.hasPermission(
  userRoles,
  ['admin', 'moderator']
)

const hasAnyRole = AuthUtils.hasAnyRoleInToken(
  accessToken,
  ['admin', 'moderator']
)
```

## 🚨 Обработка ошибок

### AuthErrorHandler

```typescript
import { AuthErrorHandler } from './auth/utils'

// Обработка ошибки
const errorHandler = new AuthErrorHandler()

errorHandler.handleError(error, {
  showNotification: true,
  logError: true,
  fallbackMessage: 'Произошла ошибка'
})
```

## 🔍 Отладка и разработка

### Включение отладки

```env
VITE_LOG_LEVEL=debug
VITE_ENABLE_DEVTOOLS=true
VITE_ENABLE_PERFORMANCE_MONITORING=true
```

### Логирование

```typescript
import { authConfig } from './auth/config'

if (authConfig.isDevelopment()) {
  console.log('Режим разработки')
}
```

## 🧪 Тестирование

### Настройка тестов

```typescript
// vitest.config.ts
export default {
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/auth/tests/setup.ts']
  }
}
```

### Пример теста

```typescript
import { describe, it, expect } from 'vitest'
import { TokenUtils } from '../utils/token.utils'

describe('TokenUtils', () => {
  it('should decode valid token', () => {
    const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    const decoded = TokenUtils.decodeToken(token)

    expect(decoded).toBeTruthy()
    expect(decoded.sub).toBe('user123')
  })
})
```

## 📱 Адаптивность

Все компоненты адаптивны и поддерживают:
- Мобильные устройства
- Планшеты
- Десктопные экраны
- Высокий DPI

## 🌐 Интернационализация

```typescript
import { authConfig } from './auth/config'

// Поддерживаемые языки
const languages = authConfig.get('supportedLanguages')

// Текущий язык
const currentLanguage = authConfig.get('defaultLanguage')
```

## 🔒 Безопасность

- Валидация всех входных данных
- Защита от CSRF атак
- Безопасное хранение токенов
- Rate limiting для API
- Шифрование чувствительных данных

## 📈 Мониторинг

### Sentry

```env
VITE_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### Google Analytics

```env
VITE_GOOGLE_ANALYTICS_ID=GA-TRACKING-ID
```

## 🚀 Production

### Сборка

```bash
npm run build
```

### Предпродакшн проверка

```bash
npm run preview
```

### Оптимизации

- Code splitting
- Lazy loading компонентов
- Service Worker для кеширования
- Оптимизация изображений

## 🤝 Вклад в проект

1. Создайте fork проекта
2. Создайте ветку для фичи (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Создайте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License.

## 🆘 Поддержка

При возникновении проблем:
1. Проверьте документацию
2. Поищите похожие issues
3. Создайте новый issue с подробным описанием

## 🔄 Обновления

Следите за обновлениями:
- Проверяйте changelog
- Обновляйте зависимости регулярно
- Следите за security advisories

---

**Создано с ❤️ для Vue.js сообщества**