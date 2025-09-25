# Техническое задание: Загрузка списка групп из TXT файла

## 1. Обзор фичи

### Цель
Реализовать функционал загрузки списка VK групп из текстового файла для последующего анализа комментариев.

### Контекст
Существующий backend на Express.js с MVC-архитектурой. Проект анализирует VK комментарии через API. Требуется добавить возможность массовой загрузки групп из файла.

## 2. Функциональные требования

### 2.1 Загрузка файла
- **Endpoint**: `POST /api/groups/upload`
- **Content-Type**: `multipart/form-data`
- **Параметры**:
  - `file`: TXT файл с группами
  - `encoding`: кодировка файла (по умолчанию: utf-8)

### 2.2 Формат файла
```
-123456789  # ID группы (отрицательное число)
-987654321  # ID группы
group_name  # Имя группы (опционально)
```

**Правила парсинга**:
- Одна группа на строку
- ID группы: отрицательное число (начинается с `-`)
- Имя группы: строка без `-` в начале (опционально)
- Пустые строки игнорируются
- Комментарии после `#` игнорируются

### 2.3 Валидация
- **Файл**: только .txt, размер до 10MB
- **ID групп**: валидные отрицательные числа
- **Дубликаты**: исключать повторяющиеся ID
- **VK API**: проверка существования групп

## 3. API Endpoints

### 3.1 Загрузка групп
```http
POST /api/groups/upload
Content-Type: multipart/form-data

{
  "file": <txt_file>,
  "encoding": "utf-8" // опционально
}
```

**Ответ**:
```json
{
  "success": true,
  "data": {
    "taskId": "uuid",
    "totalGroups": 150,
    "validGroups": 145,
    "invalidGroups": 5,
    "duplicates": 3
  }
}
```

### 3.2 Статус обработки
```http
GET /api/groups/upload/:taskId/status
```

**Ответ**:
```json
{
  "status": "completed", // created, processing, completed, failed
  "progress": {
    "processed": 145,
    "total": 150,
    "percentage": 96.7
  },
  "errors": [
    {
      "groupId": "-123456789",
      "error": "Group not found"
    }
  ]
}
```

### 3.3 Список загруженных групп
```http
GET /api/groups?taskId=uuid&limit=20&offset=0
```

**Ответ**:
```json
{
  "groups": [
    {
      "id": -123456789,
      "name": "Group Name",
      "status": "valid", // valid, invalid, duplicate
      "uploadedAt": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 145,
  "pagination": {
    "limit": 20,
    "offset": 0,
    "hasMore": true
  }
}
```

## 4. Техническая реализация

### 4.1 Структура файлов
```
backend/src/
├── controllers/
│   └── groupsController.js     # Новый контроллер
├── services/
│   └── groupsService.js        # Бизнес-логика загрузки
├── repositories/
│   └── groupsRepo.js           # Работа с БД групп
├── models/
│   └── Group.js                # Модель группы
├── utils/
│   ├── fileParser.js           # Парсинг TXT файла
│   └── vkValidator.js          # Валидация через VK API
└── middleware/
    └── upload.js               # Multer для загрузки файлов
```

### 4.2 Модель данных
```javascript
// Group.js
const Group = {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    allowNull: false
  },
  name: {
    type: DataTypes.STRING,
    allowNull: true
  },
  status: {
    type: DataTypes.ENUM('valid', 'invalid', 'duplicate'),
    defaultValue: 'valid'
  },
  taskId: {
    type: DataTypes.UUID,
    allowNull: false
  },
  uploadedAt: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW
  }
};
```

### 4.3 Асинхронная обработка
- Использовать существующий `taskService.js`
- Создать worker для валидации групп через VK API
- Rate limiting: 3 запроса/сек к VK API
- Batch processing: по 10 групп за раз

## 5. Обработка ошибок

### 5.1 Валидация файла
```javascript
// Ошибки валидации
{
  "success": false,
  "error": "INVALID_FILE",
  "message": "File must be .txt and under 10MB",
  "details": {
    "maxSize": "10MB",
    "allowedTypes": [".txt"]
  }
}
```

### 5.2 Ошибки парсинга
```javascript
{
  "success": false,
  "error": "PARSE_ERROR",
  "message": "Failed to parse file",
  "details": {
    "line": 15,
    "content": "invalid_group_id",
    "expectedFormat": "Negative integer or group name"
  }
}
```

### 5.3 VK API ошибки
```javascript
{
  "success": false,
  "error": "VK_API_ERROR",
  "message": "Failed to validate groups",
  "details": {
    "vkError": "Rate limit exceeded",
    "retryAfter": 60
  }
}
```

## 6. Безопасность

### 6.1 Валидация файлов
- Проверка MIME type
- Ограничение размера (10MB)
- Сканирование на вредоносный контент
- Временное хранение файлов

### 6.2 Rate Limiting
- 1 загрузка в минуту на IP
- 100 групп в минуту на пользователя
- VK API: 3 запроса/сек

## 7. Мониторинг и логирование

### 7.1 Логи
- Загрузка файла: размер, количество строк
- Парсинг: количество валидных/невалидных групп
- VK API: количество запросов, ошибки
- Время обработки

### 7.2 Метрики
- Количество загруженных групп
- Процент успешной валидации
- Время обработки файла
- Ошибки VK API

## 8. Тестирование

### 8.1 Unit тесты
- `fileParser.js`: парсинг различных форматов
- `vkValidator.js`: валидация ID групп
- `groupsService.js`: бизнес-логика

### 8.2 Integration тесты
- Загрузка файла через API
- Валидация через VK API
- Сохранение в БД

### 8.3 Тестовые данные
```txt
# Тестовый файл групп
-123456789  # Валидная группа
-987654321  # Валидная группа
invalid_id  # Невалидный ID
-111111111  # Дубликат
```

## 9. Развертывание

### 9.1 Миграции БД
```sql
CREATE TABLE groups (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255),
  status VARCHAR(20) DEFAULT 'valid',
  task_id UUID NOT NULL,
  uploaded_at TIMESTAMP DEFAULT NOW()
);
```

### 9.2 Переменные окружения
```env
MAX_FILE_SIZE=10485760  # 10MB
VK_API_RATE_LIMIT=3     # запросов в секунду
UPLOAD_RATE_LIMIT=1     # загрузок в минуту
```

## 10. Критерии готовности

- [ ] API endpoint для загрузки файла
- [ ] Парсинг TXT файла с валидацией
- [ ] Валидация групп через VK API
- [ ] Асинхронная обработка с прогрессом
- [ ] Сохранение в БД
- [ ] Обработка ошибок и валидация
- [ ] Unit и integration тесты
- [ ] Документация API
