# API Routes

Документ описывает основные маршруты API, их назначение, входные и выходные данные, а также правила использования.

---

## Общая информация
- Все маршруты доступны по префиксу `/api/v1/`
- Формат данных: JSON
- Аутентификация: отсутствует (или через Bearer Token, если включено)

---

## Health
- `GET /api/v1/health` — Проверка состояния сервиса
  - **Ответ:** `{ status: "ok" }`
- `GET /api/v1/info` — Информация о сервисе
  - **Ответ:** `{ name, version }`

---

## VK Groups
- `GET /api/v1/groups/` — Получить список групп
  - **Параметры:** пагинация (`page`, `size`), `active_only`
  - **Ответ:** PaginatedResponse<VKGroupRead>
- `POST /api/v1/groups/` — Добавить новую группу
  - **Тело:** VKGroupCreate
  - **Ответ:** VKGroupRead
- `GET /api/v1/groups/{group_id}` — Получить группу по ID
  - **Ответ:** VKGroupRead
- `PUT /api/v1/groups/{group_id}` — Обновить группу
  - **Тело:** VKGroupUpdate
  - **Ответ:** VKGroupRead
- `DELETE /api/v1/groups/{group_id}` — Удалить группу
  - **Ответ:** 204 No Content
- `GET /api/v1/groups/{group_id}/stats` — Статистика по группе
  - **Ответ:** VKGroupStats

---

## Keywords
- `GET /api/v1/keywords/` — Получить список ключевых слов
  - **Параметры:** пагинация, `active_only`, `category`, `q`
  - **Ответ:** PaginatedResponse<KeywordResponse>
- `POST /api/v1/keywords/` — Добавить ключевое слово
  - **Тело:** KeywordCreate
  - **Ответ:** KeywordResponse
- `GET /api/v1/keywords/{keyword_id}` — Получить ключевое слово по ID
  - **Ответ:** KeywordResponse
- `PUT /api/v1/keywords/{keyword_id}` — Обновить ключевое слово
  - **Тело:** KeywordUpdate
  - **Ответ:** KeywordResponse
- `DELETE /api/v1/keywords/{keyword_id}` — Удалить ключевое слово
  - **Ответ:** StatusResponse
- `GET /api/v1/keywords/categories` — Список категорий
  - **Ответ:** `string[]`
- `POST /api/v1/keywords/bulk` — Массовое добавление ключевых слов
  - **Тело:** KeywordCreate[]
  - **Ответ:** KeywordResponse[]

---

## Comments
- `GET /api/v1/comments/` — Получить список комментариев
  - **Параметры:** пагинация
  - **Ответ:** PaginatedResponse<VKCommentResponse>

---

## Parser
- `POST /api/v1/parser/parse` — Запустить парсинг группы
  - **Тело:** ParseTaskCreate
  - **Ответ:** ParseTaskResponse
- `GET /api/v1/parser/state` — Текущее состояние парсера
  - **Ответ:** ParserState
- `GET /api/v1/parser/stats` — Статистика парсера
  - **Ответ:** ParserStats
- `GET /api/v1/parser/tasks` — Список задач парсинга
  - **Параметры:** пагинация
  - **Ответ:** PaginatedResponse<ParseTaskResponse>
- `GET /api/v1/parser/history` — История запусков
  - **Параметры:** `skip`, `limit`
  - **Ответ:** ParseTaskResponse[]

---

## Stats
- `GET /api/v1/stats/global` — Глобальная статистика
  - **Ответ:** GlobalStats
- `GET /api/v1/stats/dashboard` — Статистика для дашборда
  - **Ответ:** DashboardStats (примерная структура)
- `GET /api/v1/stats/health` — Проверка здоровья API
  - **Ответ:** `{ success: boolean, message: string }`

---

## Примечания
- Все параметры и схемы строго типизированы (см. документацию OpenAPI/Swagger).
- Для всех POST/PUT-запросов требуется тело запроса в формате JSON.
- Ошибки возвращаются с HTTP-кодом и описанием причины.

Документ лаконичен и отражает только основные маршруты и правила их использования.
