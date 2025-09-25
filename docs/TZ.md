@# Техническое задание: страницы фронтенда для новых API

## Страница «Задачи»
- **Назначение**: управление задачами сбора данных.
- **API**: `GET /api/tasks?page&limit`, `POST /api/tasks`, `POST /api/tasks/collect`.
- **UI**: таблица задач с колонками id, тип, статус, прогресс, createdAt; пагинация; фильтр по статусу; модалки создания задач обоих типов с валидацией (ownerId < 0, postId > 0, token — обязателен; массив `groups` — только положительные числа).
- **UX**: состояния загрузки и пустого списка; обработка 4xx/5xx (тосты); после создания показывать taskId и кнопку перехода к деталям.

## Страница «Задача / Детали»
- **API**: `GET /api/tasks/:taskId`, `POST /api/collect/:taskId`, `GET /api/results/:taskId?groupId&postId`.
- **UI**: карточка статуса (status, priority, progress, metrics, timestamps), лента ошибок, JSON `result`; кнопка «Запустить» для статуса `pending`; блок фильтрации результатов по `groupId`/`postId`; таблица результатов с пагинацией.
- **UX**: опрос каждые 5–10 с для статусов `pending`/`processing`; обработка 404 («Задача не найдена»); экспорт результатов в CSV.

## Страница «Группы / Загрузка»
- **API**: `POST /api/groups/upload`, `GET /api/groups/upload/:taskId/status`.
- **UI**: форма загрузки `.txt`/`.csv`, селектор кодировки, отображение taskId; прогресс-бар (`processed/total/percentage`), список ошибок парсинга.
- **UX**: polling статуса каждые 3 с до `completed/failed`; вывод `error/message` при отказе; кнопка «Скачать отчёт об ошибках» (локальные данные).

## Страница «Группы / Список»
- **API**: `GET /api/groups?page&limit&status&search&sortBy&sortOrder`, `DELETE /api/groups/:groupId`, `DELETE /api/groups/batch`.
- **UI**: таблица с колонками groupId, name, status, uploadedAt, lastCheckedAt, errorsCount; левая панель фильтров; поиск по ID/названию; чекбоксы для массового удаления и модалки подтверждения.
- **UX**: пагинация, сортировка по заголовкам; оптимистичное обновление при удалении с fallback на ошибку.

## Страница «Группы / Статистика»
- **API**: `GET /api/groups/:taskId/stats`.
- **UI**: блок KPI (valid, invalid, duplicates), диаграммы (pie/column) по статусам, таблица проблемных групп с причинами.
- **UX**: обработка 404 с подсказкой; переход к деталям задачи.

## Общие требования
- Архитектура FSD, UI — shadcn, состояние через стор (Pinia или аналог);
- поллинг через общий сервис с очисткой при размонтировании;
- унифицированная обработка ошибок (утилита `useApiError`);
- локализация через центральный слой (ru/en);
- тесты: по одному e2e на happy-path каждой страницы; unit для валидации форм и стора.

## Улучшения backend
- Унифицировать ответы 4xx: `{errorCode, message, details}`;
- добавить rate-limit заголовки и CSRF-защиту для POST/DELETE;
- в `POST /api/tasks/collect` проверять уникальность `groups` до постановки в очередь;
- в `groupsService.cleanupFile` не удалять исходный буфер (сейчас возможен двойной `unlink`).