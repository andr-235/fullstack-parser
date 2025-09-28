# Фронтенд для системы анализа VK комментариев

Этот проект — фронтенд на Vue 3 для системы анализа комментариев из VK API. Он предоставляет удобный интерфейс для запуска задач по сбору и анализу комментариев, мониторинга статуса и просмотра результатов. Фронтенд интегрируется с backend на Node.js/Express через REST API и использует Vuetify для UI, Pinia для состояния и Axios для запросов.

Подробное техническое задание: [docs/TZ.md](docs/TZ.md).

## Рекомендуемая среда разработки

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (отключите Vetur).

## Настройка конфигурации

См. [Справочник по конфигурации Vite](https://vite.dev/config/).

## Установка и запуск

### Установка зависимостей

```sh
npm install
```

Зависимости (из [package.json](package.json)):
- **Основные**: `vue@^3.5.18`, `vue-router@^4.5.1`, `pinia@^3.0.3`, `axios@^1.12.2`, `vuetify@3.4.0`, `@mdi/font@^7.4.47`.
- **Dev-зависимости**: `vite@^7.0.6`, `vitest@^3.2.4`, `@playwright/test@^1.54.1`, `eslint@^9.31.0`, `prettier@3.6.2`.

### Запуск в режиме разработки (с hot-reload)

```sh
npm run dev
```

Сервер запустится на `http://localhost:5173`. В режиме разработки запросы к `/api` проксируются на backend (`http://localhost:3000`) через [vite.config.js](vite.config.js).

Для явного запуска в режиме разработки с локальным бэкендом используйте:
```sh
npm run dev:local
```

Для переключения в режим разработки убедитесь, что в файле `.env` или `.env.development` установлена переменная `VITE_API_URL=http://localhost:3000`.

### Сборка для production

```sh
npm run build
```

Сгенерированные файлы в `dist/`. Для деплоя используйте Nginx (см. раздел "Интеграция с backend").

### Проверка типов

```sh
npm run type-check          # Проверка TypeScript типов
npm run type-check:watch    # Проверка типов в режиме watch
```

### Линтинг и форматирование

```sh
npx eslint .                # Линтинг кода
npx prettier --write .      # Форматирование кода
```

## Использование

Фронтенд состоит из страниц (views), компонентов и сторов. Все на русском языке, responsive (Vuetify), с валидацией форм, toast-уведомлениями и обработкой ошибок.

### Основные страницы

- **/fetch** ([src/views/FetchComments.vue](src/views/FetchComments.vue)): Форма для запуска задачи.
  - Поля: `ownerId` (ID сообщества, e.g. -123), `postId` (ID поста, e.g. 456).
  - Кнопка "Запустить задачу" отправляет POST на `/api/tasks`.
  - Успех: Показ taskId, редирект на `/task/:taskId`.
  - Пример: Заполните форму и нажмите кнопку — получите ID задачи для мониторинга.

- **/tasks/:taskId** ([src/views/TaskDetailsView.vue](src/views/TaskDetailsView.vue)): Детали задачи и мониторинг статуса.
  - Polling каждые 5 сек на GET `/api/tasks/:taskId`.
  - Отображает статус (Ожидание, Обработка, Завершено, Ошибка), прогресс.
  - При завершении: Редирект на `/comments?taskId=...`.
  - Пример: Перейдите по `/task/abc-123` — увидите обновления в реальном времени.

- **/comments** ([src/views/CommentsList.vue](src/views/CommentsList.vue)): Список комментариев.
  - GET `/api/comments` с фильтрами (taskId, postId, sentiment, limit=20, offset).
  - Таблица: текст (кликабельный), автор, дата, sentiment (цвет: зеленый/серый/красный), keywords (чипы).
  - Фильтры: Поиск по тексту, dropdown для sentiment, пагинация.
  - Пример: Добавьте `?taskId=abc-123` в URL — загрузится список с анализом.

### Аутентификация

- Токен VK загружается в backend из переменных окружения.

### Компоненты

- [ErrorMessage.vue](src/components/ErrorMessage.vue): Отображение ошибок.
- [LoadingSpinner.vue](src/components/LoadingSpinner.vue): Спиннеры загрузки.

### Сторы (Pinia)

- [auth.js](src/stores/auth.js): Токен, login/logout.
- [tasks.js](src/stores/tasks.js): Статус задач.
- [comments.js](src/stores/comments.js): Список, фильтры.

Пример навигации: Откройте `http://localhost:5173/fetch`, запустите задачу, перейдите на `/comments`.

## Интеграция с backend

Backend — Node.js/Express приложение с BullMQ для асинхронных задач, PostgreSQL/Redis. Доступен по `http://localhost:3000`.

### Эндпоинты API

- `POST /api/tasks`: `{ "ownerId": -123, "postId": 456 }` → `{ "taskId": "uuid" }`.
- `GET /api/tasks/:taskId`: `{ "status": "completed", "progress": 100 }`.
- `GET /api/comments?taskId=uuid&limit=20&offset=0`: `{ "comments": [...], "total": 100 }`.

Подробности в [docs/TZ.md](docs/TZ.md) (раздел "Примеры API запросов").

### Запуск backend

В корне проекта:
```sh
docker-compose up
```

Это запустит PostgreSQL (5432), Redis (6379), backend (3000), worker. Настройте `.env` для секретов (DB_URL, VK_TOKEN).

В dev-режиме фронтенда proxy автоматически перенаправляет `/api` на backend. Для production: Соберите фронтенд (`npm run build`), добавьте Nginx в docker-compose (прокси `/api` на backend:3000, статические файлы из dist/).

Пример nginx.conf:
```
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    location /api {
        proxy_pass http://backend:3000;
    }
}
```

## Тестирование

### Unit-тесты (Vitest)

```sh
npx vitest                  # Запуск unit тестов
npx vitest --ui             # Запуск с UI интерфейсом
npx vitest --coverage       # Запуск с отчетом о покрытии
```

Тесты для views, components, stores (>80% покрытие). Примеры: [src/views/__tests__/FetchComments.spec.js](src/views/__tests__/FetchComments.spec.js).

### E2E-тесты (Playwright)

```sh
# Установка браузеров (первый запуск)
npx playwright install

# Сборка проекта (для CI)
npm run build

# Запуск тестов
npx playwright test

# Только Chromium
npx playwright test --project=chromium

# Конкретный файл
npx playwright test e2e/vue.spec.js

# Debug-режим
npx playwright test --debug
```

Тесты сценариев: авторизация, запуск задачи, просмотр списка. Файлы: [e2e/vue.spec.js](e2e/vue.spec.js).

## Вклад в проект

- Форкните репозиторий.
- Создайте ветку: `git checkout -b feature/имя`.
- Коммитьте: `git commit -m "feat: добавлена функция"`.
- Пушьте и создайте PR.

Используйте Conventional Commits. Линтинг и тесты обязательны перед PR.

## Лицензия

MIT.