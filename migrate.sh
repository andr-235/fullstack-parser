#!/bin/bash

# Название docker-compose файла и сервисов
COMPOSE_FILE="docker-compose.prod.ip.yml"
BACKEND_SERVICE="backend"

echo "🚀 Применяем все миграции Alembic внутри контейнера $BACKEND_SERVICE..."

docker-compose -f $COMPOSE_FILE exec $BACKEND_SERVICE alembic upgrade head

STATUS=$?
if [ $STATUS -eq 0 ]; then
  echo "✅ Миграции успешно применены!"
else
  echo "❌ Ошибка при применении миграций!"
  exit $STATUS
fi
