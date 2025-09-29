# Процесс загрузки групп из файла

1. **Выбор/загрузка файла в UI**: В GroupsUploadForm.vue пользователь выбирает TXT/CSV файл (до 10 МБ) через input или drag&drop, указывает кодировку (UTF-8 по умолчанию). Валидация: обязательность, расширение, размер. Ошибки: alert с сообщением (неверный тип/размер).

2. **Отправка на backend**: FormData с файлом отправляется POST /api/groups/upload?encoding=... через api.ts (axios с multipart). Retry при 429. Ошибки: сетевые/серверные -> catch в handleUpload, alert.

3. **Обработка файла**: Middleware upload.ts (multer): парсит buffer, фильтрует тип (.txt), лимит 10 МБ/1 файл. Validate: наличие, размер, UTF-8. Затем groupsController.ts вызывает groupsService.uploadGroups(buffer, encoding). Ошибки: 400 (multer/validate), log.

4. **Валидация ID групп via vkIoService.ts**: FileParser.ts парсит строки (URL clubID, -ID, ID, screen_name). groupsService.processGroupsAsync: VKValidator (если токен) проверяет ID, vkIoService.getGroupsInfo обогащает данными (name, members и т.д.). Fallback при ошибке VK. Ошибки: invalid ID -> invalidGroups с error; API fail -> warn log, базовые данные.

5. **Сохранение уникальных групп в DB**: groupsRepo.groupExistsByVkId проверяет дубликаты. Уникальные: upsert в groups (vk_id unique, status 'valid', task_id UUID). Schema: model groups с полями vk_id, name и т.д. Ошибки: duplicate -> count++, invalid; DB fail -> throw, status 'failed'.

6. **Обновление UI/статус**: Создается taskId, Map хранит статус (created->processing->completed/failed) с progress (%). GET /api/groups/upload/:taskId/status возвращает статус/errors. Frontend polling via groupsApi.getTaskStatus, emit 'upload-started', обновление stores/groups.ts. Ошибки: task not found -> 404; failed -> errors в response.