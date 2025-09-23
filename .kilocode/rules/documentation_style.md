# Правила стиля документации

## Обзор

Эти правила определяют стандарты написания документации для обеспечения ясности, последовательности и профессионализма. Они применяются ко всем типам документации в проекте, включая README, API-документацию, коммит-сообщения и внутренние документы для fullstack JS/TS проекта (Node.js/Express backend, Vue.js frontend).

## Общие принципы

- **Язык**: Использовать русский язык для основной документации, английский для технических терминов и кодовых примеров.
- **Формат**: Использовать Markdown для всех документов.
- **Структура**: Документы должны иметь четкую структуру с заголовками, списками и разделами.
- **Актуальность**: Регулярно обновлять документацию при изменениях в коде.
- **Доступность**: Документация должна быть понятной для всех уровней разработчиков.

## README

- **Структура**:
  - Краткое описание проекта (backend для анализа VK, frontend для UI).
  - Установка и запуск (npm install, docker-compose up).
  - Использование (примеры API calls, Vue views).
  - API (эндпоинты Express).
  - Frontend (Vue components, Pinia stores).
  - Вклад в проект.
  - Лицензия.
- **Рекомендации**:
  - Начинать с краткого описания цели проекта (анализ комментариев VK).
  - Включать примеры команд: `npm install`, `docker-compose up`.
  - Добавлять скриншоты Vue UI или диаграммы архитектуры.
  - Указывать версии зависимостей (Node.js, Vue 3, Express).

## API-документация

- **Формат**: Использовать OpenAPI/Swagger для REST API в Express.
- **Элементы**:
  - Описание эндпоинтов (e.g., POST /api/tasks).
  - Параметры запроса и ответа (JSON schemas).
  - Примеры запросов (curl или axios).
  - Коды ошибок (400, 500).
- **Рекомендации**:
  - Описывать каждый эндпоинт подробно (e.g., fetchComments).
  - Включать примеры JSON: `{ "ownerId": 1, "postId": 1 }`.
  - Указывать типы данных (string, number) и ограничения (required).
  - Документировать аутентификацию (VK tokens via headers) и авторизацию.

Пример Swagger для Express:
```yaml
paths:
  /api/tasks:
    post:
      summary: Создать задачу на сбор комментариев
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                ownerId: { type: number }
                postId: { type: number }
      responses:
        '200':
          description: ID задачи
          content:
            application/json:
              schema:
                type: object
                properties:
                  taskId: { type: number }
```

## Коммит-сообщения

- **Формат**: Использовать Conventional Commits.
  - `type(scope): description`
- **Типы**:
  - `feat`: новая функциональность (e.g., feat(vk): add comments fetching).
  - `fix`: исправление ошибок.
  - `docs`: изменения в документации.
  - `style`: форматирование кода.
  - `refactor`: рефакторинг.
  - `test`: добавление тестов.
  - `chore`: обслуживание.
- **Рекомендации**:
  - Писать на английском языке.
  - Описывать изменения кратко и ясно (e.g., "fix(backend): handle VK API rate limit").
  - Избегать общих сообщений типа "fix bug".
  - Указывать номер задачи, если применимо (e.g., feat(frontend): add TaskStatus view #123).

## Внутренняя документация

- **Код**: Добавлять JSDoc к функциям, классам и модулям.
- **Модули**: Вести README для сложных модулей (e.g., services/vkService.js).
- **Архитектура**: Документировать архитектурные решения (MVC-like, async tasks).
- **Рекомендации**:
  - Использовать JSDoc формат с @param, @returns, @example.
  - Включать описание параметров, возвращаемых значений и исключений.
  - Добавлять примеры использования (e.g., для Express routes).

Пример JSDoc:
```javascript
/**
 * Получает комментарии из VK.
 * @param {number} ownerId - ID владельца поста
 * @param {number} postId - ID поста
 * @returns {Promise<Array>} Массив комментариев
 * @example
 * const comments = await fetchComments(1, 1);
 */
async function fetchComments(ownerId, postId) { ... }
```

## Документация проекта

- **Обзор**: Описывать цели (анализ VK комментариев) и архитектуру (Express + Vue + PostgreSQL/Redis).
- **Установка**: Подробные инструкции: `npm install` в backend/frontend, `docker-compose up`.
- **Разработка**: Руководство для контрибьюторов (ESLint, тесты Jest/Vitest).
- **Рекомендации**:
  - Вести changelog для отслеживания изменений (e.g., v1.0.0: initial VK integration).
  - Документировать известные проблемы (VK rate limits) и ограничения.
  - Включать глоссарий терминов (e.g., taskService: async processing).

## Инструменты

- **Генерация**: Использовать JSDoc для кода, MkDocs для сайта документации.
- **Хранение**: Хранить документацию в репозитории проекта (docs/ folder).
- **Рекомендации**:
  - Автоматизировать генерацию в CI/CD (GitHub Actions: jsdoc, mkdocs build).
  - Проверять орфографию и грамматику (e.g., markdownlint).
  - Использовать инструменты для проверки ссылок (e.g., markdown-link-check).