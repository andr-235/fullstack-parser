# Comment Entity

Бизнес-сущность комментария из VK.

## Структура

```
entities/comment/
├── model.ts      # Модель комментария с бизнес-логикой
├── types.ts      # TypeScript типы
├── hooks.ts      # React хуки для работы с API
└── index.ts      # Публичный API
```

## Модель Comment

### Свойства

- `id: number` - уникальный идентификатор
- `text: string` - текст комментария
- `authorId: number` - ID автора
- `authorName?: string` - имя автора
- `publishedAt: string` - дата публикации
- `vkId: number` - ID в VK
- `postId: number` - ID поста
- `likesCount: number` - количество лайков
- `hasAttachments: boolean` - есть ли вложения
- `matchedKeywordsCount: number` - количество совпавших ключевых слов
- `isProcessed: boolean` - обработан ли комментарий
- `isViewed: boolean` - просмотрен ли комментарий
- `isArchived: boolean` - архивирован ли комментарий

### Методы

- `get isOverdue(): boolean` - просрочен ли комментарий
- `get formattedPublishedAt(): string` - отформатированная дата
- `get status(): 'new' | 'viewed' | 'archived'` - статус комментария

### Статические методы

- `static fromAPI(data: VKCommentResponse): Comment` - создание из API данных
- `static fromAPIWithKeywords(data: CommentWithKeywords): Comment` - создание с ключевыми словами

## Типы

### VKCommentResponse

Ответ API для комментария.

### CommentWithKeywords

Комментарий с детальной информацией о ключевых словах.

### CommentSearchParams

Параметры поиска комментариев.

## Хуки

### useComments

Получение комментариев с пагинацией.

```typescript
const { data, isLoading, error } = useComments({
  text: 'поиск',
  group_id: 1,
  page: 1,
  size: 20,
})
```

### useInfiniteComments

Бесконечная загрузка комментариев.

```typescript
const { data, isLoading, isFetchingNextPage, hasNextPage, fetchNextPage } =
  useInfiniteComments({ text: 'поиск' })
```

### useMarkCommentAsViewed

Отметка комментария как просмотренного.

```typescript
const markAsViewed = useMarkCommentAsViewed()
await markAsViewed.mutateAsync(commentId)
```

### useArchiveComment

Архивирование комментария.

```typescript
const archive = useArchiveComment()
await archive.mutateAsync(commentId)
```

### useUnarchiveComment

Разархивирование комментария.

```typescript
const unarchive = useUnarchiveComment()
await unarchive.mutateAsync(commentId)
```

## Использование

```typescript
import { Comment, useComments } from '@/entities/comment'

// Создание модели
const comment = new Comment(apiData)

// Использование хуков
const { data } = useComments()
```

## Валидация

Модель автоматически валидирует данные при создании и предоставляет типизированные методы для работы с комментариями.
