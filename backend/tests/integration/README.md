# Интеграционные тесты VK Comments Parser

Этот каталог содержит интеграционные тесты для проверки взаимодействия компонентов системы.

## Структура тестов

### `test_api_integration.py`

Базовые интеграционные тесты API endpoints:

- ✅ Проверка доступности всех API endpoints
- ✅ Тестирование health check системы
- ✅ Валидация обработки ошибок
- ✅ Проверка CORS заголовков
- ✅ Тестирование логирования запросов

### `test_groups_workflow.py`

Интеграционные тесты полного цикла работы с группами:

- ✅ Создание групп
- ✅ Импорт групп из файлов
- ✅ Валидация групп через VK API
- ✅ Работа с ключевыми словами
- ✅ Поиск и анализ комментариев
- ✅ Полная интеграция всех компонентов

### `test_performance.py`

Тесты производительности системы:

- ✅ Время отклика API endpoints
- ✅ Производительность запросов к БД
- ✅ Массовые операции
- ✅ Одновременные запросы
- ✅ Использование памяти
- ✅ Пул соединений БД

## Запуск тестов

### Запуск всех интеграционных тестов

```bash
cd /opt/app/backend
python -m pytest tests/integration/ -v
```

### Запуск конкретного тестового файла

```bash
# API интеграция
python -m pytest tests/integration/test_api_integration.py -v

# Workflow групп
python -m pytest tests/integration/test_groups_workflow.py -v

# Производительность
python -m pytest tests/integration/test_performance.py -v
```

### Запуск с маркерами

```bash
# Только быстрые тесты
python -m pytest tests/integration/ -m "not slow" -v

# Только тесты производительности
python -m pytest tests/integration/ -m performance -v
```

### Запуск с отчетом о покрытии

```bash
python -m pytest tests/integration/ --cov=app --cov-report=html -v
```

## Конфигурация тестов

### `conftest.py`

Содержит конфигурацию для интеграционных тестов:

- ✅ Асинхронные фикстуры
- ✅ Тестовая база данных (SQLite)
- ✅ HTTP клиент для API тестирования
- ✅ Автоматический rollback транзакций
- ✅ Настройка логирования

## Фикстуры

### Основные фикстуры

- `client` - HTTP клиент для тестирования API
- `db_session` - Сессия базы данных с автоматическим rollback
- `test_engine` - Тестовый engine базы данных

### Сервисные фикстуры

- `group_manager` - Менеджер групп
- `comment_service` - Сервис комментариев
- `keyword_service` - Сервис ключевых слов
- `vk_service` - VK API сервис

## Правила написания тестов

### 1. Асинхронность

Все тесты должны быть асинхронными:

```python
async def test_example(self, client):
    response = await client.get("/api/v1/example")
    assert response.status_code == 200
```

### 2. Использование фикстур

Используйте фикстуры для зависимостей:

```python
async def test_with_db(self, db_session, group_manager):
    group = await group_manager.create_group(db_session, {...})
    assert group is not None
```

### 3. Маркеры

Используйте маркеры для категоризации:

```python
@pytest.mark.performance
@pytest.mark.slow
async def test_slow_performance_test(self):
    # Тест производительности
```

### 4. Assert сообщения

Добавляйте понятные сообщения в assert:

```python
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
```

## Производительность

### Пороги производительности

- **API response time**: < 2.0 сек
- **DB query time**: < 1.0 сек
- **Bulk operation time**: < 5.0 сек
- **Concurrent requests**: < 5.0 сек для 10 запросов

### Мониторинг

Тесты автоматически проверяют:

- Время выполнения запросов
- Заголовки `X-Process-Time`
- Использование памяти
- Стабильность запросов к БД

## Отладка

### Логирование

Тесты используют структурированное логирование. Для отладки:

```bash
# Включить подробное логирование
python -m pytest tests/integration/ -v -s --log-cli-level=INFO
```

### Отдельный запуск

```bash
# Запуск одного теста
python -m pytest tests/integration/test_api_integration.py::TestAPIIntegration::test_api_root_endpoint -v -s
```

## CI/CD интеграция

Тесты автоматически запускаются в CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Run Integration Tests
  run: |
    cd backend
    python -m pytest tests/integration/ -v --tb=short
```

## Полезные команды

```bash
# Показать все доступные тесты
python -m pytest tests/integration/ --collect-only

# Запуск с профилированием
python -m pytest tests/integration/ --profile

# Запуск с повторением упавших тестов
python -m pytest tests/integration/ --reruns 3

# Параллельный запуск
python -m pytest tests/integration/ -n auto
```

## Расширение тестов

### Добавление новых тестов

1. Создайте новый файл `test_*.py`
2. Наследуйтесь от базового класса
3. Используйте существующие фикстуры
4. Добавьте маркеры при необходимости

### Добавление новых фикстур

1. Добавьте в `conftest.py`
2. Используйте scope `function` или `session`
3. Добавьте документацию

## Контакты

При проблемах с тестами:

1. Проверьте логи приложения
2. Убедитесь что база данных доступна
3. Проверьте конфигурацию в `conftest.py`
