#!/bin/bash

# Скрипт для активации Poetry окружения
echo "Активируем Poetry окружение..."

# Проверяем, что мы в правильной директории
if [ ! -f "pyproject.toml" ]; then
    echo "Ошибка: pyproject.toml не найден. Перейдите в директорию backend/"
    exit 1
fi

# Активируем виртуальное окружение
echo "Используем Python из Poetry окружения..."
poetry env use python3.11

# Показываем информацию об окружении
echo "Информация об окружении:"
poetry env info

# Проверяем зависимости
echo "Проверяем зависимости..."
poetry run python -c "import structlog, vkbottle; print('✅ Все зависимости установлены')"

echo "Окружение готово! Используйте 'poetry run python' для запуска скриптов"
echo "Или 'poetry run uvicorn app.main:app --reload' для запуска FastAPI" 