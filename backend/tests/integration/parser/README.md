# Parser Module Integration Tests

Этот пакет содержит комплексные интеграционные тесты для модуля Parser, которые проверяют взаимодействие компонентов, производительность и надежность системы.

## Структура тестов

### 1. Workflow Integration (`test_parser_workflow.py`)

Проверяет полный цикл работы парсера:

- ✅ Полный pipeline парсинга от запроса до результата
- ✅ Взаимодействие между компонентами
- ✅ Поток данных через систему
- ✅ Управление состоянием операций

### 2. API Integration (`test_parser_api.py`)

Тестирует HTTP API endpoints:

- ✅ Сериализация запросов/ответов
- ✅ HTTP статус коды
- ✅ Форматирование ошибок
- ✅ CORS и заголовки

### 3. Performance Integration (`test_parser_performance.py`)

Анализирует производительность:

- ✅ Время отклика
- ✅ Использование памяти
- ✅ Загрузка CPU
- ✅ Масштабируемость

### 4. Error Recovery Integration (`test_parser_error_recovery.py`)

Проверяет обработку ошибок:

- ✅ Восстановление после сетевых сбоев
- ✅ Обработка лимитов API
- ✅ Частичные сбои
- ✅ Исчерпание ресурсов

### 5. Load Testing Integration (`test_parser_load.py`)

Тестирует поведение под нагрузкой:

- ✅ Конкурентные запросы
- ✅ Большие датасеты
- ✅ Управление очередью
- ✅ Шаблоны использования ресурсов

## Запуск тестов

### Все интеграционные тесты

```bash
cd /opt/app/backend
poetry run pytest tests/integration/parser/ -v
```

### Конкретная категория

```bash
# Workflow тесты
poetry run pytest tests/integration/parser/test_parser_workflow.py -v

# API тесты
poetry run pytest tests/integration/parser/test_parser_api.py -v

# Performance тесты
poetry run pytest tests/integration/parser/test_parser_performance.py -v

# Error recovery тесты
poetry run pytest tests/integration/parser/test_parser_error_recovery.py -v

# Load тесты
poetry run pytest tests/integration/parser/test_parser_load.py -v
```

### С дополнительными опциями

```bash
# С профилированием производительности
poetry run pytest tests/integration/parser/ --profile-svg

# С подробным выводом
poetry run pytest tests/integration/parser/ -v -s

# Только failed тесты
poetry run pytest tests/integration/parser/ --lf

# С покрытием кода
poetry run pytest tests/integration/parser/ --cov=src.parser --cov-report=html
```

## Конфигурация тестов

### Test Fixtures (conftest.py)

```python
# Mock сервисы
mock_vk_api_service          # Mock VK API
integration_parser_service   # ParserService для интеграции

# Тестовые данные
sample_vk_api_responses      # Образцы ответов VK API
integration_test_data        # Полный набор тестовых данных

# Конфигурации
performance_test_config      # Настройки performance тестов
load_test_config            # Настройки load тестов
error_simulation_config     # Настройки симуляции ошибок
```

### Performance Benchmarks

```
✅ Response Time:      < 100ms (single operation)
✅ Memory Usage:       < 100MB (during load)
✅ CPU Utilization:    < 80% (average)
✅ Throughput:         > 10 ops/sec
✅ Error Rate:         < 5% (normal load)
✅ Concurrent Users:   > 20 (simultaneous)
```

## Архитектура тестов

### Test Data Flow

```
Request → ParserService → VK API → Response
    ↓         ↓            ↓        ↓
Validation → Processing → External → Serialization
    ↓         ↓            ↓        ↓
   Logs →   Metrics →   Cache →   Client
```

### Error Handling

```
Network Error → Retry → Circuit Breaker → Fallback
Rate Limit   → Backoff → Queue → Recovery
Resource Exhaustion → Cleanup → Scaling → Recovery
```

### Performance Monitoring

```
Response Time → Histogram → Percentiles → Alerts
Memory Usage → Time Series → Thresholds → Cleanup
CPU Load → Utilization → Scaling → Optimization
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run Integration Tests
  run: |
    cd backend
    poetry run pytest tests/integration/parser/ -v \
      --cov=src.parser \
      --cov-report=xml \
      --junitxml=integration-results.xml

- name: Performance Regression Check
  run: |
    # Check if performance degraded > 10%
    poetry run pytest tests/integration/parser/test_parser_performance.py \
      --benchmark-save=baseline
```

### Docker Integration

```dockerfile
# Integration test stage
FROM python:3.11-slim as integration-tests

COPY . /app
WORKDIR /app/backend

RUN poetry install --with dev
RUN poetry run pytest tests/integration/parser/ \
  --cov=src.parser \
  --cov-report=term-missing \
  --durations=10
```

## Мониторинг и отладка

### Логирование

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# В тестах
with caplog.at_level(logging.DEBUG):
    # Test code that produces logs
    pass
```

### Профилирование

```python
import cProfile
pr = cProfile.Profile()
pr.enable()
# Test code
pr.disable()
pr.print_stats(sort='time')
```

## Расширение тестов

### Добавление нового тестового сценария

```python
class TestNewIntegrationScenario:
    """New integration test scenario"""

    @pytest.mark.asyncio
    async def test_new_scenario(self, setup_integration_environment):
        env = await setup_integration_environment
        service = env["service"]

        # Test implementation
        result = await service.some_new_method()
        assert result["status"] == "success"
```

### Добавление performance benchmark

```python
def test_performance_benchmark(self, benchmark):
    @benchmark
    def run_operation():
        # Operation to benchmark
        return self.service.process_data()
```

## Troubleshooting

### Common Issues

1. **Timeout Errors**

   ```bash
   # Increase timeout
   pytest --timeout=300 tests/integration/parser/
   ```

2. **Memory Issues**

   ```bash
   # Run with limited concurrency
   pytest -n 2 tests/integration/parser/
   ```

3. **External Service Failures**
   ```bash
   # Use offline mode
   pytest --disable-warnings tests/integration/parser/
   ```

### Debug Mode

```bash
# Verbose output with captures
pytest -v -s --capture=no tests/integration/parser/test_parser_workflow.py::TestParserWorkflowIntegration::test_full_parsing_workflow

# PDB on failure
pytest --pdb tests/integration/parser/
```

## Contributing

### Code Standards

- Все тесты должны иметь docstrings
- Использовать descriptive имена
- Группировать связанные тесты в классы
- Добавлять performance assertions где возможно

### Test Categories

- `test_*` - функциональные тесты
- `test_*_performance` - performance тесты
- `test_*_load` - нагрузочные тесты
- `test_*_error` - тесты обработки ошибок

### Documentation

- Обновлять этот README при добавлении новых тестов
- Добавлять примеры использования
- Документировать performance expectations
