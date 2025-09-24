# Правила конвенций именования

## Обзор

Эти правила определяют конвенции именования для JavaScript/TypeScript проектов, основанные на лучших практиках (Airbnb style guide). Соблюдение этих правил обеспечивает читаемость, поддерживаемость и согласованность кода в backend (Node.js/Express) и frontend (Vue.js).

## Переменные

- Использовать `camelCase` для имен переменных.
- Примеры:
  - `userName`
  - `totalCount`
  - `isActive`

## Функции и методы

- Использовать `camelCase` для имен функций и методов.
- Примеры:
  - `getUserData()`
  - `calculateTotal()`
  - `validateInput()`

## Классы

- Использовать `PascalCase` для имен классов.
- Примеры:
  - `UserModel`
  - `DatabaseConnection`
  - `ApiClient`

## Константы

- Использовать `UPPER_SNAKE_CASE` для констант.
- Примеры:
  - `MAX_RETRY_COUNT`
  - `DEFAULT_TIMEOUT`
  - `API_VERSION`

## Файлы и модули

- Использовать `kebab-case` или `camelCase` для имен файлов и модулей.
- Расширения: `.js`, `.ts`, `.vue`
- Примеры:
  - `user-model.js`
  - `database-utils.js`
  - `TaskStatus.vue`

## Пакеты и директории

- Использовать `kebab-case` для имен пакетов и директорий.
- Примеры:
  - `src/models`
  - `src/services`
  - `node_modules`

## Приватные переменные и методы

- Начинать с подчеркивания для приватных переменных и методов: `_privateVar`
- Примеры:
  - `_internalCounter`
  - `_hiddenMethod()`

## Специальные методы

- Для lifecycle методов в классах использовать стандартные имена (e.g., `constructor`, `render` в Vue).
- Примеры:
  - `constructor()`
  - `componentDidMount()`

## Исключения

- Использовать `PascalCase` и заканчивать на `Error`.
- Примеры:
  - `ValidationError`
  - `DatabaseError`

## Переменные окружения

- Использовать `UPPER_SNAKE_CASE` для переменных окружения.
- Примеры:
  - `DATABASE_URL`
  - `VK_TOKEN`

## Рекомендации

- Избегать однобуквенных имен, кроме счетчиков в циклах (i, j, k).
- Использовать описательные имена, отражающие назначение.
- Для сокращений использовать общепринятые формы (e.g., `url` вместо `uniformResourceLocator`).
- Соблюдать длину имен: не слишком короткие, но и не чрезмерно длинные.

Пример для Express route:
```javascript
// routes/taskRoutes.js
const express = require('express');
const router = express.Router();
const taskController = require('../controllers/taskController');

router.post('/tasks', taskController.createTask);
```

Пример для Vue компонента:
```vue
<!-- components/CommentsList.vue -->
<script setup>
import { computed } from 'vue';
import { useCommentsStore } from '@/stores/comments';

const commentsStore = useCommentsStore();
const filteredComments = computed(() => commentsStore.comments);
</script>