# Group Entity

Бизнес-сущность VK группы.

## Структура

```
entities/group/
├── model.ts      # Модель группы с бизнес-логикой
├── types.ts      # TypeScript типы
├── hooks.ts      # React хуки для работы с API
└── index.ts      # Публичный API
```

## Модель Group

### Свойства

- `id: number` - уникальный идентификатор
- `vkId: number` - ID в VK
- `screenName: string` - короткое имя группы
- `name: string` - название группы
- `description?: string` - описание группы
- `isActive: boolean` - активна ли группа
- `maxPostsToCheck: number` - максимальное количество постов для проверки
- `lastParsedAt?: string` - дата последнего парсинга
- `totalPostsParsed: number` - общее количество обработанных постов
- `totalCommentsFound: number` - общее количество найденных комментариев
- `membersCount?: number` - количество участников
- `isClosed: boolean` - закрыта ли группа
- `photoUrl?: string` - URL фотографии группы

### Методы

- `get isRecentlyActive(): boolean` - активна ли группа недавно
- `get formattedLastParsedAt(): string` - отформатированная дата последнего парсинга
- `get vkUrl(): string` - URL группы в VK
- `get status(): 'active' | 'inactive' | 'closed'` - статус группы

### Статические методы

- `static fromAPI(data: VKGroupResponse): Group` - создание из API данных

## Типы

### VKGroupResponse

Ответ API для группы.

### VKGroupCreate

Данные для создания группы.

### VKGroupUpdate

Данные для обновления группы.

## Хуки

### useGroups

Получение списка групп с пагинацией.

```typescript
const { data, isLoading, error } = useGroups({
  active_only: true,
  search: 'поиск',
  page: 1,
  size: 20,
})
```

### useGroup

Получение конкретной группы.

```typescript
const { data, isLoading, error } = useGroup(groupId)
```

### useCreateGroup

Создание новой группы.

```typescript
const createGroup = useCreateGroup()
await createGroup.mutateAsync({
  vk_id_or_screen_name: 'group_name',
  is_active: true,
  max_posts_to_check: 10,
})
```

### useUpdateGroup

Обновление группы.

```typescript
const updateGroup = useUpdateGroup()
await updateGroup.mutateAsync({
  groupId: 1,
  data: { is_active: false },
})
```

### useDeleteGroup

Удаление группы.

```typescript
const deleteGroup = useDeleteGroup()
await deleteGroup.mutateAsync(groupId)
```

### useGroupStats

Получение статистики группы.

```typescript
const { data, isLoading } = useGroupStats(groupId)
```

## Использование

```typescript
import { Group, useGroups } from '@/entities/group'

// Создание модели
const group = new Group(apiData)

// Использование хуков
const { data } = useGroups({ active_only: true })
```

## Валидация

Модель автоматически валидирует данные при создании и предоставляет типизированные методы для работы с группами.
