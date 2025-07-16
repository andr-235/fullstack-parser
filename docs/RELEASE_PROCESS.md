# 🚀 Процесс релизов

Данный документ описывает процесс создания и управления релизами в проекте.

## 📋 Обзор

Наш процесс релизов основан на **семантическом версионировании** (SemVer) и автоматизирован через GitHub Actions. Каждый релиз проходит через полный цикл тестирования, сборки и деплоя.

## 🏷️ Семантическое версионирование

Мы используем формат `MAJOR.MINOR.PATCH`:

- **MAJOR** (x.0.0) - Критические изменения, несовместимые с предыдущими версиями
- **MINOR** (0.x.0) - Новые функции, обратная совместимость
- **PATCH** (0.0.x) - Исправления багов, мелкие улучшения

### Примеры версий:
- `1.0.0` - Первый стабильный релиз
- `1.2.0` - Добавлены новые функции
- `1.2.3` - Исправлены баги
- `1.2.3-beta.1` - Бета-версия
- `1.2.3-rc.1` - Release Candidate

## 🔄 Процесс создания релиза

### 1. Автоматический способ (рекомендуется)

Используйте наш скрипт для создания релизов:

```bash
# Переход в корень проекта
cd /opt/app

# Запуск скрипта создания релиза
./scripts/create-release.sh
```

Скрипт проведет вас через интерактивный процесс:
1. Выбор типа релиза (major/minor/patch/prerelease)
2. Автоматическое обновление версий в файлах
3. Создание тега и push
4. Создание GitHub Release

### 2. Ручной способ

```bash
# 1. Обновить версии в файлах
# backend/pyproject.toml
# frontend/package.json

# 2. Создать коммит
git add .
git commit -m "chore: bump version to 1.2.3"

# 3. Создать тег
git tag -a v1.2.3 -m "Release v1.2.3"

# 4. Отправить тег
git push origin v1.2.3
```

### 3. Через GitHub UI

1. Перейти в **Releases** на GitHub
2. Нажать **"Create a new release"**
3. Выбрать тег или создать новый
4. Заполнить описание
5. Опубликовать

## 🛠️ GitHub Actions Workflow

При создании тега автоматически запускается workflow `release-enhanced.yml`:

### Этапы процесса:

1. **🛡️ Validate Release** - Валидация версии и параметров
2. **🔒 Security Scan** - Сканирование уязвимостей (Trivy)
3. **📦 Dependency Check** - Проверка зависимостей
4. **🐍 Backend Tests** - Тестирование backend с покрытием
5. **⚛️ Frontend Tests** - Тестирование frontend с покрытием
6. **🐳 Build and Push** - Сборка и публикация Docker образов
7. **🎉 Create Release** - Создание GitHub Release с changelog
8. **🚀 Deploy Staging** - Деплой на staging окружение
9. **📢 Notify Team** - Уведомления команды
10. **🧹 Cleanup** - Очистка артефактов

### Docker образы

Каждый релиз создает следующие образы:
- `ghcr.io/andr-235/backend:VERSION`
- `ghcr.io/andr-235/frontend:VERSION`
- `ghcr.io/andr-235/arq-worker:VERSION`

Также создаются теги:
- `latest` - Последняя стабильная версия
- `MAJOR.MINOR` - Минорная версия
- `MAJOR` - Мажорная версия
- `sha-XXXXX` - SHA коммита

## 📝 Changelog

Автоматически генерируется на основе:
- Pull Request с лейблами
- Issues с лейблами
- Conventional Commits

### Категории:
- 🚀 **Features** - Новые функции
- 🐛 **Bug Fixes** - Исправления багов
- 📄 **Documentation** - Документация
- 🧪 **Testing** - Тесты
- ⚙️ **Miscellaneous** - Прочие изменения

## 🔧 Конфигурация

### Переменные окружения

В GitHub Secrets должны быть настроены:
- `GHCR_TOKEN` - Токен для GitHub Container Registry
- `CODECOV_TOKEN` - Токен для Codecov (опционально)
- `SLACK_WEBHOOK_URL` - Webhook для Slack уведомлений (опционально)

### Environments

Настроены следующие environments:
- `staging` - Тестовое окружение
- `production` - Продакшен окружение

## 🚨 Принудительный релиз

В экстренных случаях можно создать принудительный релиз:

1. Через GitHub Actions UI:
   - Перейти в Actions → Enhanced Release & Publish
   - Нажать "Run workflow"
   - Ввести версию
   - Поставить галочку "force"

2. Через скрипт:
   ```bash
   # Создать тег вручную
   git tag -a v1.2.3 -m "Emergency release"
   git push origin v1.2.3
   ```

Принудительный релиз пропускает:
- Security scan
- Dependency check
- Некоторые тесты

## 📊 Мониторинг релизов

### Отслеживание прогресса:
- GitHub Actions: https://github.com/andr-235/fullstack-parser/actions
- Releases: https://github.com/andr-235/fullstack-parser/releases
- Docker Hub: https://github.com/andr-235/fullstack-parser/pkgs/container/backend

### Метрики:
- Время сборки
- Покрытие тестами
- Количество уязвимостей
- Успешность деплоя

## 🔄 Rollback

В случае проблем с релизом:

### 1. Откат Docker образов:
```bash
# На сервере
docker-compose -f docker-compose.prod.ip.yml up -d --remove-orphans PREVIOUS_VERSION
```

### 2. Откат базы данных:
```bash
# Восстановление из backup
./scripts/restore_db.sh backup/YYYY-MM-DD_HH-MM-SS.sql
```

### 3. Откат кода:
```bash
# Создание hotfix
git checkout -b hotfix/rollback-v1.2.3
git revert v1.2.3
git push origin hotfix/rollback-v1.2.3
```

## 📋 Checklist перед релизом

- [ ] Все тесты проходят
- [ ] Линтеры не выдают ошибок
- [ ] Документация обновлена
- [ ] Changelog сгенерирован
- [ ] Версии обновлены во всех файлах
- [ ] Staging деплой протестирован
- [ ] Команда уведомлена о релизе

## 🆘 Troubleshooting

### Частые проблемы:

1. **Workflow не запускается**
   - Проверить формат тега (должен быть v*.*.*)
   - Проверить права доступа к репозиторию

2. **Docker build fails**
   - Проверить Dockerfile
   - Проверить зависимости
   - Проверить размер контекста

3. **Tests fail**
   - Проверить изменения в коде
   - Проверить тестовые данные
   - Проверить конфигурацию тестов

4. **Deploy fails**
   - Проверить secrets
   - Проверить доступ к серверу
   - Проверить docker-compose файл

## 📞 Поддержка

При возникновении проблем:
1. Проверить логи GitHub Actions
2. Обратиться к команде разработки
3. Создать issue с описанием проблемы

## 🔗 Полезные ссылки

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Docker Hub](https://docs.docker.com/docker-hub/)
- [Trivy Security Scanner](https://aquasecurity.github.io/trivy/)
