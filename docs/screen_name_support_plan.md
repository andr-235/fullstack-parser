# План поддержки парсинга групп по screen_name

## Обзор проблемы
Текущая система парсит URL "https://vk.com/club467927" (с ID) нормально, но для "https://vk.com/priamursk" (screen_name без club) парсер устанавливает id: null, name: "priamursk". В groupsService при резолве в ID name перезаписывается пустой строкой, что приводит к потере оригинального screen_name для закрытых групп (fallback "Группа ID").

## Текущая логика
- FileParser.parseGroupLine:
  - Ловит "https://vk.com/club\d+" -> id: число.
  - Ловит "https://vk.com/[a-zA-Z0-9_]+" -> id: null, name: screen_name.
  - Поддерживает отрицательные ID, положительные числа, "club\d+".
- groupsService.processGroupsAsync:
  - Резолвит screen_name через vkIoService.resolveScreenNames (g.name как screen_name).
  - В enrichedGroups: name = vkInfo.name || "Группа ID" (пустой для screen_name).
  - Сохраняет screen_name в БД.

## Решение
- В groupsService: сохранить originalScreenName из ParsedGroup (name в FileParser).
- В enrichedGroups: name = vkInfo.name || originalScreenName.
- Обеспечить, что screen_name сохраняется в БД для всех случаев.
- Backward compatibility: ID-группы не затрагиваются.

## Диаграмма workflow
```mermaid
graph TD
    A[FileParser: парсинг URL] --> B{id == null?}
    B -->|да, screen_name| C[groupsService: резолв в ID, сохранить originalScreenName]
    C --> D[vkIoService.getGroupsInfo]
    D --> E[enrichedGroups: name = vkInfo.name || originalScreenName]
    E --> F[groupsRepo: сохранить vk_id, screen_name, name]
    B -->|нет, ID| F
```

## Шаги реализации
1. Обновить FileParser.parseGroupsFile: возвращать originalScreenName в ProcessedGroup (уже есть как name при id: null).
2. В groupsService.processGroupsAsync: при создании groupsWithScreenNames сохранять screenName: g.name.
3. В цикле резолва: передать screenName в resolvedMap или отдельный Map.
4. В enrichedGroups: name = vkInfo.name || screenName.
5. Обновить типы: ProcessedGroup добавить originalScreenName?: string (опционально).
6. Тесты: unit для парсера, integration для workflow с примерами "https://vk.com/priamursk".
7. Docs: добавить примеры в groups-upload-process.md.

## Важные замечания
- Rate limiting: resolveScreenNames уже батчит с задержкой 350ms.
- Производительность: для больших файлов (>1000 строк) добавить кэш резолвов в Redis.
- Ошибки: если резолв fails, сохранить с error: "Failed to resolve screen_name", name = originalScreenName.

План готов к реализации в code mode.