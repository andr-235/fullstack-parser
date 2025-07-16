# 🚀 Упрощённый CI/CD для одного разработчика

## 📋 Обзор

Эта система CI/CD оптимизирована для работы одного разработчика. Убраны лишние проверки, упрощён процесс деплоя, добавлены быстрые команды.

## 🎯 Основные принципы

- **Быстрые проверки** - только критичные тесты
- **Прямой деплой** - без staging, сразу в production
- **Автоматические теги** - по коммитам в main
- **Простой workflow** - минимум сложности

## 🚀 Быстрый старт

### 1. Запуск разработки

```bash
make dev
# или
docker compose up -d
```

### 2. Тесты

```bash
make test
# или
./scripts/quick-deploy.sh  # включает тесты
```

### 3. Деплой в production

```bash
make deploy
# или
./scripts/quick-deploy.sh
```

## 📁 Структура файлов

```
.github/workflows/
├── simple-ci.yml          # Упрощённый CI/CD
├── ci.yml                 # Старый сложный CI (можно отключить)
└── deploy-production.yml  # Старый деплой (можно отключить)

scripts/
└── quick-deploy.sh        # Скрипт быстрого деплоя

Makefile.simple            # Упрощённые команды
```

## 🔧 Команды Makefile

### Основные команды

```bash
make dev      # Запуск в режиме разработки
make test     # Быстрые тесты
make build    # Сборка образов
make deploy   # Деплой в production
make status   # Статус сервисов
make logs     # Показать логи
make clean    # Очистка Docker
```

### Git команды

```bash
make branch   # Создать новую ветку
make commit   # Коммит изменений
make push     # Пуш в репозиторий
make pr       # Создать Pull Request
```

## 🔄 Workflow

### Обычная разработка

1. `make branch` - создать ветку
2. Разработка
3. `make test` - проверить тесты
4. `make commit` - коммит
5. `make push` - пуш
6. `make pr` - создать PR
7. Merge в main

### Быстрый деплой

1. Переключиться на main: `git checkout main`
2. `./scripts/quick-deploy.sh` - быстрый деплой
3. Автоматический деплой через GitHub Actions

## ⚡ CI/CD Pipeline

### Триггеры

- Push в `main` → автоматический деплой
- Push в `develop` → только тесты
- Pull Request → только тесты

### Этапы

1. **Быстрые тесты** (10 мин)

   - Backend: pytest с ограничением ошибок
   - Frontend: Jest тесты

2. **Сборка и деплой** (15 мин)
   - Создание тега (дата + коммит)
   - Сборка Docker образов
   - Пуш в GitHub Container Registry
   - Деплой на сервер
   - Создание GitHub Release

## 🏷️ Система тегов

Автоматические теги создаются в формате:

```
v20241201-a1b2c3d
```

Где:

- `20241201` - дата (YYYYMMDD)
- `a1b2c3d` - короткий хеш коммита

## 🔧 Настройка

### Secrets (уже настроены)

- `PRODUCTION_HOST` - IP сервера
- `PRODUCTION_USER` - пользователь SSH
- `PRODUCTION_SSH_KEY` - SSH ключ
- `PRODUCTION_APP_DIR` - директория приложения
- `GHCR_USERNAME` - GitHub Container Registry
- `GHCR_TOKEN` - токен для GHCR
- `NEXT_PUBLIC_API_URL` - URL API для frontend

### Отключение старого CI/CD

Если хочешь использовать только упрощённую версию:

1. Переименуй старые файлы:

```bash
mv .github/workflows/ci.yml .github/workflows/ci.yml.backup
mv .github/workflows/deploy-production.yml .github/workflows/deploy-production.yml.backup
```

2. Переименуй новый файл:

```bash
mv .github/workflows/simple-ci.yml .github/workflows/ci.yml
```

## 🚨 Откат деплоя

### Быстрый откат

```bash
# На сервере
cd /opt/app
docker compose -f docker-compose.prod.ip.yml up -d --build <PREVIOUS_TAG>
```

### Через GitHub

1. Перейти в Releases
2. Найти предыдущий релиз
3. Скопировать тег
4. Запустить деплой с этим тегом

## 📊 Мониторинг

### GitHub Actions

- https://github.com/andr-235/fullstack/actions

### Статус сервисов

```bash
make status
# или
docker compose ps
```

### Логи

```bash
make logs
# или
docker compose logs -f
```

## 🎯 Преимущества

✅ **Быстрота** - деплой за 15-20 минут
✅ **Простота** - минимум настроек
✅ **Надёжность** - основные проверки сохранены
✅ **Автоматизация** - теги и релизы создаются автоматически
✅ **Мониторинг** - понятные логи и статусы

## 🔄 Миграция со старого CI/CD

1. Протестируй новый workflow на develop
2. Переключись на новый workflow
3. Отключи старые файлы
4. Обнови документацию команды

## 🆘 Troubleshooting

### Тесты падают

```bash
# Локальная проверка
make test

# Детальные логи
cd backend && poetry run pytest tests/ -v
cd frontend && pnpm test --verbose
```

### Деплой не запускается

1. Проверь что в main ветке
2. Проверь что нет незакоммиченных изменений
3. Проверь GitHub Actions

### Образы не собираются

```bash
# Локальная сборка
make build

# Проверка Docker
docker images | grep fullstack
```

## 📞 Поддержка

При проблемах:

1. Проверь логи: `make logs`
2. Проверь статус: `make status`
3. Очисти кэш: `make clean`
4. Перезапусти: `make dev`
