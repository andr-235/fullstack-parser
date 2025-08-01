# VK Parser Frontend

Angular приложение для работы с VK Parser API.

## Настройка API

### Backend API Endpoints

Backend использует NestJS с префиксом `/api/v1`. Основные эндпоинты:

#### Groups

- `GET /api/v1/groups` - Получить список групп
- `POST /api/v1/groups` - Создать группу
- `GET /api/v1/groups/:id` - Получить группу по ID
- `PATCH /api/v1/groups/:id` - Обновить группу
- `DELETE /api/v1/groups/:id` - Удалить группу

#### Keywords

- `GET /api/v1/keywords` - Получить список ключевых слов
- `POST /api/v1/keywords` - Создать ключевое слово
- `GET /api/v1/keywords/:id` - Получить ключевое слово по ID
- `PATCH /api/v1/keywords/:id` - Обновить ключевое слово
- `DELETE /api/v1/keywords/:id` - Удалить ключевое слово

#### Comments

- `GET /api/v1/comments` - Получить список комментариев
- `GET /api/v1/comments/:id` - Получить комментарий по ID
- `PATCH /api/v1/comments/:id` - Обновить комментарий

### Параметры запросов

#### Groups

- `page` - Номер страницы (по умолчанию 1)
- `limit` - Количество элементов на странице (по умолчанию 20)
- `search` - Поиск по названию группы
- `isActive` - Фильтр по активным группам

#### Keywords

- `page` - Номер страницы
- `limit` - Количество элементов на странице
- `search` - Поиск по слову
- `isActive` - Фильтр по активным ключевым словам

#### Comments

- `page` - Номер страницы
- `limit` - Количество элементов на странице
- `search` - Поиск по тексту комментария
- `groupId` - Фильтр по группе
- `hasKeywords` - Фильтр комментариев с ключевыми словами

### Структура данных

#### CreateVKGroupDto (Backend)

```typescript
{
  vkId: number;
  screenName: string;
  name: string;
  description?: string;
}
```

#### CreateKeywordDto (Backend)

```typescript
{
  word: string;
  isActive?: boolean;
}
```

### Настройка окружения

В `environment.ts` и `environment.prod.ts` установлен правильный API URL:

```typescript
export const environment = {
  production: false,
  apiUrl: "http://localhost:8000/api/v1",
  appName: "VK Parser Frontend",
};
```

### Запуск

1. Убедитесь что backend запущен на порту 8000
2. Запустите frontend:

```bash
ng serve
```

Приложение будет доступно по адресу `http://localhost:4200`
