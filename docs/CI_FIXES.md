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

## Коммиты

- `56e377c` - fix: обновление CI для frontend тестов - pnpm 10.12.4 и Node.js 20
- `42bb6be` - fix: обновление конфигурации Jest для лучшей производительности 