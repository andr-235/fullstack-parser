#!/bin/bash

# Названия контейнера, пользователя и базы — подставь свои, если отличаются!
CONTAINER=fullstack_postgres_prod
DB=vk_parser
USER=postgres

# Заходим в контейнер и дропаем базу
docker exec -it $CONTAINER psql -U $USER -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB';"
docker exec -it $CONTAINER psql -U $USER -c "DROP DATABASE IF EXISTS $DB;"
docker exec -it $CONTAINER psql -U $USER -c "CREATE DATABASE $DB;"

echo "✅ База $DB успешно пересоздана!"
