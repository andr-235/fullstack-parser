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
    sudo apt-get install -y redis-server redis-tools
    
    # Проверяем конфигурацию Redis
    echo "🔧 Настройка Redis..."
    
    # Создаем директорию для данных Redis если не существует
    sudo mkdir -p /var/lib/redis
    sudo chown redis:redis /var/lib/redis
    
    # Проверяем права на конфигурационный файл
    if [ -f /etc/redis/redis.conf ]; then
        sudo chown redis:redis /etc/redis/redis.conf
        # Убеждаемся что Redis слушает на localhost
        sudo sed -i 's/^bind 127.0.0.1/bind 127.0.0.1/' /etc/redis/redis.conf
    fi
    
    # Останавливаем если уже запущен
    sudo systemctl stop redis-server 2>/dev/null || true
    
    # Запускаем Redis
    echo "▶️ Запуск Redis..."
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    # Ждем немного для запуска
    sleep 2
    
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
    echo "🔍 Проверка Redis..."
    if redis-cli ping 2>/dev/null | grep -q PONG; then
        echo "✅ Redis доступен"
    else
        echo "⚠️ Redis не отвечает через systemctl, пробуем альтернативный запуск..."
        
        # Показываем статус для диагностики
        echo "📋 Статус Redis:"
        sudo systemctl status redis-server --no-pager || true
        
        # Пробуем запустить Redis вручную в фоне
        echo "🔄 Пробуем запустить Redis вручную..."
        sudo pkill redis-server 2>/dev/null || true
        sleep 1
        
        # Запуск Redis в фоне
        sudo -u redis redis-server /etc/redis/redis.conf --daemonize yes 2>/dev/null || \
        sudo redis-server /etc/redis/redis.conf --daemonize yes 2>/dev/null || \
        redis-server --daemonize yes --port 6379 --bind 127.0.0.1 2>/dev/null &
        
        sleep 3
        
        # Проверяем еще раз
        if redis-cli ping 2>/dev/null | grep -q PONG; then
            echo "✅ Redis доступен (запущен вручную)"
        else
            echo "❌ Redis недоступен даже после ручного запуска"
            echo "💡 Попробуйте запустить вручную: redis-server --port 6379"
            exit 1
        fi
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
