# 🚀 Быстрый старт: VK Comments Parser

## ✅ Что уже готово

**Backend полностью функционален!** 

- ✅ FastAPI приложение с async/await
- ✅ PostgreSQL база данных с миграциями
- ✅ VK API интеграция
- ✅ Парсинг комментариев с фильтрацией по ключевым словам
- ✅ REST API для управления группами и ключевыми словами
- ✅ Docker контейнеризация
- ✅ Автоматическая документация API

## 🔧 Следующие шаги

### 1. Получение VK Access Token

Для работы с VK API нужен токен:

1. Перейдите на https://vk.com/apps?act=manage
2. Создайте Standalone приложение
3. Получите access_token с правами `groups,wall`
4. Обновите `.env` файл:

```bash
VK_ACCESS_TOKEN=ваш-настоящий-токен-здесь
```

### 2. Тестирование API

**Backend уже запущен на http://localhost:8000**

Доступные endpoints:
- 📊 **Документация**: http://localhost:8000/docs
- 🏥 **Health Check**: http://localhost:8000/health  
- 🔗 **API Root**: http://localhost:8000/api/v1/

#### Основные операции:

**Добавить ключевые слова:**
```bash
curl -X POST http://localhost:8000/api/v1/keywords/ \
  -H "Content-Type: application/json" \
  -d '{"word": "python", "category": "programming", "is_active": true}'
```

**Добавить VK группу:**
```bash
curl -X POST http://localhost:8000/api/v1/groups/ \
  -H "Content-Type: application/json" \
  -d '{
    "vk_id_or_screen_name": "python",
    "name": "Python Community",
    "is_active": true,
    "max_posts_to_check": 50
  }'
```

**Запустить парсинг:**
```bash
curl -X POST http://localhost:8000/api/v1/parser/parse \
  -H "Content-Type: application/json" \
  -d '{"group_id": 1, "max_posts": 10}'
```

**Посмотреть найденные комментарии:**
```bash
curl http://localhost:8000/api/v1/parser/comments/
```

### 3. Создание Frontend (опционально)

Если нужен веб-интерфейс, можно создать:

```bash
# В новом терминале
mkdir frontend
cd frontend
npx create-next-app@latest . --typescript --tailwind --eslint --app
```

## 📊 API Документация

Автоматическая документация доступна:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Полезные команды

**Перезапуск сервисов:**
```bash
docker-compose restart backend
```

**Просмотр логов:**
```bash
docker-compose logs -f backend
```

**Остановка всех сервисов:**
```bash
docker-compose down
```

**Полная очистка (удаление данных):**
```bash
docker-compose down -v
```

## 📝 Примеры использования

### Сценарий 1: Мониторинг Python сообществ

1. Добавить ключевые слова: "python", "django", "fastapi", "машинное обучение"
2. Добавить группы: "python", "nuancesprog", "proglib"
3. Запустить парсинг каждой группы
4. Просмотреть найденные комментарии

### Сценарий 2: Поиск вакансий

1. Добавить ключевые слова: "вакансия", "ищем", "работа", "зарплата"
2. Добавить IT группы
3. Настроить автоматический парсинг

## 🔐 Безопасность

- Никогда не коммитьте реальный VK токен в Git
- Используйте `.env` файл для секретных данных
- В production смените `SECRET_KEY` и пароли БД

## 🚀 Production Deployment

Для деплоя на сервер:
```bash
# На сервере
git clone ваш-репозиторий
cd fullstack_parser
cp env.example .env.prod
# Отредактировать .env.prod с production настройками
docker-compose -f docker-compose.prod.yml up -d
```

## 🆘 Troubleshooting

**Ошибка подключения к VK API:**
- Проверьте правильность токена
- Убедитесь, что токен имеет нужные права (groups, wall)

**Ошибка базы данных:**
- Перезапустите контейнеры: `docker-compose restart`
- Проверьте логи: `docker-compose logs postgres`

**Нет найденных комментариев:**
- Проверьте активность ключевых слов
- Убедитесь, что группа активна
- Проверьте логи парсинга 