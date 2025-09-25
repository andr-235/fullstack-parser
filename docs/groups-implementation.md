# Реализация страниц управления группами VK

## Обзор

Реализован полный функционал управления группами VK согласно техническому заданию `groups-vue-tz.md`.

## Структура файлов

### Store
- `src/stores/groups.js` - Pinia store для управления состоянием групп

### API
- `src/services/api.js` - Добавлены методы `groupsApi` для работы с группами

### Компоненты
- `src/components/groups/FileUploader.vue` - Drag & Drop загрузчик файлов
- `src/components/groups/GroupsTable.vue` - Таблица групп с пагинацией
- `src/components/groups/GroupsFilters.vue` - Фильтры и поиск
- `src/components/groups/TaskProgress.vue` - Прогресс обработки задач

### Страницы
- `src/views/groups/GroupsUpload.vue` - Страница загрузки файла
- `src/views/groups/GroupsList.vue` - Список групп
- `src/views/groups/GroupsTaskStatus.vue` - Статус задачи

### Роутинг
- Добавлены маршруты в `src/router/index.js`:
  - `/groups` - список групп
  - `/groups/upload` - загрузка файла
  - `/groups/task/:taskId` - статус задачи

### Навигация
- Обновлен `src/components/Sidebar.vue` с пунктом "Группы VK"

## Функциональность

### ✅ Загрузка файла
- Drag & Drop интерфейс
- Валидация файла (размер, тип)
- Выбор кодировки (UTF-8, Windows-1251, KOI8-R)
- Прогресс-бар загрузки

### ✅ Управление группами
- Таблица с пагинацией (20 групп на страницу)
- Фильтрация по статусу (valid, invalid, duplicate)
- Поиск по ID группы или названию
- Сортировка по дате загрузки, статусу
- Удаление групп

### ✅ Мониторинг задач
- Real-time обновление статуса (polling каждые 2 сек)
- Прогресс-бар обработки
- Список ошибок валидации
- Автоматическое перенаправление при завершении

## API Endpoints

```javascript
// Загрузка файла
POST /api/groups/upload
Content-Type: multipart/form-data
Body: { file: File, encoding: string }

// Статус задачи
GET /api/groups/upload/:taskId/status

// Список групп
GET /api/groups?page=1&limit=20&status=all&search=&sortBy=uploadedAt&sortOrder=desc

// Удаление группы
DELETE /api/groups/:groupId

// Массовое удаление
DELETE /api/groups/batch
Body: { groupIds: string[] }
```

## Типы данных

```typescript
interface Group {
  id: number
  name?: string
  status: 'valid' | 'invalid' | 'duplicate'
  taskId: string
  uploadedAt: string
}

interface TaskStatus {
  status: 'created' | 'processing' | 'completed' | 'failed'
  progress: {
    processed: number
    total: number
    percentage: number
  }
  errors: Array<{
    groupId: string
    error: string
  }>
}
```

## Использование

1. Перейти в раздел "Группы VK" в боковом меню
2. Нажать "Загрузить группы" для загрузки TXT файла
3. Выбрать файл и кодировку
4. Отслеживать прогресс обработки
5. Просматривать результаты в таблице групп

## Особенности реализации

- Использование Vue 3 Composition API
- Pinia для управления состоянием
- Vuetify 3 для UI компонентов
- Debounced поиск для оптимизации
- Автоматический polling для мониторинга задач
- Обработка ошибок и валидация
- Десктопный дизайн
