# Keyword Entity

Бизнес-сущность ключевого слова для поиска.

## Структура

```
entities/keyword/
├── model.ts      # Модель ключевого слова с бизнес-логикой
├── types.ts      # TypeScript типы
├── hooks.ts      # React хуки для работы с API
└── index.ts      # Публичный API
```

## Модель Keyword

### Свойства

- `id: number` - уникальный идентификатор
- `word: string` - ключевое слово
- `category?: string` - категория ключевого слова
- `description?: string` - описание
- `isActive: boolean` - активно ли ключевое слово
- `isCaseSensitive: boolean` - чувствительно ли к регистру
- `isWholeWord: boolean` - искать только целые слова
- `totalMatches: number` - общее количество совпадений

### Методы

- `get isHighPriority(): boolean` - высокий ли приоритет
- `get isMediumPriority(): boolean` - средний ли приоритет
- `get isLowPriority(): boolean` - низкий ли приоритет
- `get priority(): 'high' | 'medium' | 'low'` - приоритет ключевого слова
- `get searchPattern(): RegExp` - регулярное выражение для поиска
- `matches(text: string): boolean` - проверяет совпадение в тексте

### Статические методы

- `static fromAPI(data: KeywordResponse): Keyword` - создание из API данных

## Типы

### KeywordResponse

Ответ API для ключевого слова.

### KeywordCreate

Данные для создания ключевого слова.

### KeywordUpdate

Данные для обновления ключевого слова.

## Хуки

### useKeywords

Получение списка ключевых слов с пагинацией.

```typescript
const { data, isLoading, error } = useKeywords({
  active_only: true,
  category: 'spam',
  q: 'поиск',
  page: 1,
  size: 20,
})
```

### useKeyword

Получение конкретного ключевого слова.

```typescript
const { data, isLoading, error } = useKeyword(keywordId)
```

### useKeywordCategories

Получение списка категорий.

```typescript
const { data, isLoading } = useKeywordCategories()
```

### useCreateKeyword

Создание нового ключевого слова.

```typescript
const createKeyword = useCreateKeyword()
await createKeyword.mutateAsync({
  word: 'спам',
  category: 'spam',
  is_active: true,
  is_case_sensitive: false,
  is_whole_word: true,
})
```

### useCreateKeywordsBulk

Массовое создание ключевых слов.

```typescript
const createBulk = useCreateKeywordsBulk()
await createBulk.mutateAsync([
  { word: 'спам', category: 'spam' },
  { word: 'реклама', category: 'ads' },
])
```

### useUpdateKeyword

Обновление ключевого слова.

```typescript
const updateKeyword = useUpdateKeyword()
await updateKeyword.mutateAsync({
  id: 1,
  data: { is_active: false },
})
```

### useDeleteKeyword

Удаление ключевого слова.

```typescript
const deleteKeyword = useDeleteKeyword()
await deleteKeyword.mutateAsync(keywordId)
```

### useUploadKeywordsFromFile

Загрузка ключевых слов из файла.

```typescript
const uploadKeywords = useUploadKeywordsFromFile()
await uploadKeywords.mutateAsync(file)
```

## Использование

```typescript
import { Keyword, useKeywords } from '@/entities/keyword'

// Создание модели
const keyword = new Keyword(apiData)

// Проверка совпадения
const matches = keyword.matches('Этот текст содержит спам')

// Использование хуков
const { data } = useKeywords({ active_only: true })
```

## Приоритеты

Ключевые слова автоматически получают приоритет на основе:

- **Высокий**: частота совпадений > 100
- **Средний**: частота совпадений 10-100
- **Низкий**: частота совпадений < 10

## Валидация

Модель автоматически валидирует данные при создании и предоставляет типизированные методы для работы с ключевыми словами.
