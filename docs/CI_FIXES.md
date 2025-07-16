# CI/CD Fixes для Frontend Тестов

## Проблема
Frontend тесты падали в CI/CD pipeline, в то время как backend тесты проходили успешно.

## Исправления

### 1. Обновление GitHub Actions Workflow (.github/workflows/test.yml)

- **Версия pnpm**: Обновлена с `run_install: false` до `version: 10.12.4` для соответствия версии в package.json
- **Версия Node.js**: Обновлена с 18 до 20 для лучшей совместимости
- **Cache path**: Исправлен путь к pnpm-lock.yaml с `**/pnpm-lock.yaml` на `frontend/pnpm-lock.yaml`
- **Переменные окружения**: Добавлены `NEXT_PUBLIC_API_URL` и `CI=true` для правильной работы тестов

### 2. Обновление Jest Configuration (frontend/jest.config.js)

- **Удален transform**: Убран ручной transform для TypeScript, так как next/jest обрабатывает это автоматически
- **Добавлены moduleFileExtensions**: Указаны поддерживаемые расширения файлов
- **Настроены testPathIgnorePatterns**: Исключены .next/ и node_modules/ из тестирования
- **Добавлен collectCoverageFrom**: Настроен сбор покрытия кода

### 3. Результат

- **Производительность**: Время выполнения тестов сократилось с ~11 секунд до ~2 секунд
- **Стабильность**: Тесты теперь проходят как локально, так и в CI/CD
- **Совместимость**: Полная совместимость с Next.js 14 и pnpm 10.12.4

## Дополнительные рекомендации

1. При обновлении pnpm в package.json обязательно обновляйте версию в workflow
2. Убедитесь, что переменные окружения корректно настроены для CI
3. Регулярно проверяйте совместимость версий Node.js и Next.js

## Кэширование Docker-слоёв для локальных buildx-билдов

Для ускорения локальной сборки Docker-образов используйте buildx с локальным кэшем:

### 1. Включите buildx (если ещё не включён)
```
docker buildx create --use
```

### 2. Собирайте образы с кэшем:
```
docker buildx build \
  --cache-from=type=local,src=.docker-cache \
  --cache-to=type=local,dest=.docker-cache,mode=max \
  -t <image_name> \
  -f <Dockerfile> .
```

- `.docker-cache` — директория для хранения кэша (можно добавить в `.gitignore`).
- `<image_name>` — имя вашего образа.
- `<Dockerfile>` — путь к Dockerfile (например, `backend/Dockerfile`).

### 3. Пример для backend:
```
docker buildx build \
  --cache-from=type=local,src=.docker-cache \
  --cache-to=type=local,dest=.docker-cache,mode=max \
  -t fullstack-backend:dev \
  -f backend/Dockerfile backend
```

### 4. Пример для frontend:
```
docker buildx build \
  --cache-from=type=local,src=.docker-cache \
  --cache-to=type=local,dest=.docker-cache,mode=max \
  -t fullstack-frontend:dev \
  -f frontend/Dockerfile frontend
```

**Важно:**
- Кэш работает только при использовании buildx.
- Для очистки кэша: `rm -rf .docker-cache`.
- Добавьте `.docker-cache` в `.gitignore`.

## Новые возможности CI/CD (2024)

- Кэширование зависимостей Poetry, pnpm, Docker buildx (см. выше)
- Dependency scan: poetry check, pip-audit, pnpm audit (см. workflows/ci.yml)
- Telegram-уведомления о деплое (см. workflows/deploy-production.yml)
- Минимальные права для всех jobs (permissions: contents: read)
- Параллелизм и fail-fast для matrix jobs (strategy.fail-fast: false)
- Все reusable workflows вынесены в отдельные файлы для DRY

### Для разработчиков
- Используйте buildx с локальным кэшем для ускорения Docker-сборки (см. выше)
- Для проверки зависимостей локально: poetry check, pip-audit, pnpm audit
- Для тестов: pytest (backend), pnpm test (frontend)
- Для деплоя: используйте pull request и следите за уведомлениями в Telegram

## Коммиты

- `56e377c` - fix: обновление CI для frontend тестов - pnpm 10.12.4 и Node.js 20
- `42bb6be` - fix: обновление конфигурации Jest для лучшей производительности
