#!/bin/bash

# Скрипт настройки локального окружения для self-hosted runner
# Устанавливает PostgreSQL и Redis нативно на сервере

set -e

echo "🚀 Настройка локального окружения для разработки..."

# Проверяем операционную систему
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "📋 Обнаружена Linux система"
    
    # Обновляем пакеты
    echo "📦 Обновление пакетов..."
    sudo apt-get update
    
    # Устанавливаем PostgreSQL
    echo "🐘 Установка PostgreSQL..."
    sudo apt-get install -y postgresql postgresql-contrib
    
    # Запускаем PostgreSQL
    echo "▶️ Запуск PostgreSQL..."
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    # Настраиваем пользователя и базу данных
    echo "👤 Настройка пользователя PostgreSQL..."
    sudo -u postgres psql -c "CREATE USER postgres WITH SUPERUSER;" || echo "Пользователь postgres уже существует"
    sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
    sudo -u postgres psql -c "CREATE DATABASE vk_parser;" || echo "База vk_parser уже существует"
    sudo -u postgres psql -c "CREATE DATABASE test_db;" || echo "База test_db уже существует"
    
    # Устанавливаем Redis
    echo "📦 Установка Redis..."
    sudo apt-get install -y redis-server
    
    # Запускаем Redis
    echo "▶️ Запуск Redis..."
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    # Проверяем подключения
    echo "🔍 Проверка подключений..."
    
    # Проверяем PostgreSQL
    if pg_isready -h localhost -p 5432; then
        echo "✅ PostgreSQL доступен"
    else
        echo "❌ PostgreSQL недоступен"
        exit 1
    fi
    
    # Проверяем Redis
    if redis-cli ping | grep -q PONG; then
        echo "✅ Redis доступен"
    else
        echo "❌ Redis недоступен"
        exit 1
    fi
    
    echo "🎉 Локальное окружение настроено успешно!"
    echo ""
    echo "📝 Информация о сервисах:"
    echo "   PostgreSQL: localhost:5432"
    echo "   Redis: localhost:6379"
    echo ""
    echo "🔧 Для запуска проекта используйте:"
    echo "   docker-compose -f docker-compose.local.yml up -d"
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📋 Обнаружена macOS система"
    
    # Проверяем наличие Homebrew
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew не найден. Установите его сначала: https://brew.sh"
        exit 1
    fi
    
    # Устанавливаем PostgreSQL
    echo "🐘 Установка PostgreSQL..."
    brew install postgresql@15
    brew services start postgresql@15
    
    # Настраиваем базы данных
    createdb vk_parser || echo "База vk_parser уже существует"
    createdb test_db || echo "База test_db уже существует"
    
    # Устанавливаем Redis
    echo "📦 Установка Redis..."
    brew install redis
    brew services start redis
    
    echo "🎉 Локальное окружение настроено успешно!"
    
else
    echo "❌ Неподдерживаемая операционная система: $OSTYPE"
    echo "Поддерживаются только Linux и macOS"
    exit 1
fi
