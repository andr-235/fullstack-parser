#!/bin/bash

# Управление сервисами PostgreSQL и Redis в Docker

set -e

SERVICES_COMPOSE="docker-compose.services.yml"

case "$1" in
    start)
        echo "🚀 Запуск сервисов PostgreSQL и Redis..."
        
        # Останавливаем существующие контейнеры
        echo "🛑 Остановка существующих контейнеров..."
        docker-compose -f $SERVICES_COMPOSE down 2>/dev/null || true
        
        # Проверяем занятые порты и останавливаем процессы
        echo "🔍 Проверка портов..."
        if netstat -tlnp 2>/dev/null | grep -q ":5435 "; then
            echo "⚠️ Порт 5435 занят, останавливаем PostgreSQL процессы..."
            sudo pkill -f postgres 2>/dev/null || true
            sleep 2
        fi
        
        if netstat -tlnp 2>/dev/null | grep -q ":6379 "; then
            echo "⚠️ Порт 6379 занят, останавливаем Redis процессы..."
            sudo pkill -f redis 2>/dev/null || true
            sleep 2
        fi
        
        # Запускаем сервисы
        docker-compose -f $SERVICES_COMPOSE up -d
        
        echo "⏳ Ожидание готовности сервисов..."
        docker-compose -f $SERVICES_COMPOSE exec postgres pg_isready -U postgres || {
            echo "⏳ Ждем PostgreSQL..."
            sleep 5
            docker-compose -f $SERVICES_COMPOSE exec postgres pg_isready -U postgres
        }
        
        docker-compose -f $SERVICES_COMPOSE exec redis redis-cli ping || {
            echo "⏳ Ждем Redis..."
            sleep 5
            docker-compose -f $SERVICES_COMPOSE exec redis redis-cli ping
        }
        
        echo "✅ Все сервисы запущены и готовы!"
        echo "📋 Подключения:"
        echo "   PostgreSQL (main): localhost:5435"
        echo "   PostgreSQL (test): localhost:5434"
        echo "   Redis: localhost:6379"
        ;;
        
    stop)
        echo "🛑 Остановка сервисов..."
        docker-compose -f $SERVICES_COMPOSE down
        echo "✅ Сервисы остановлены"
        ;;
        
    restart)
        echo "🔄 Перезапуск сервисов..."
        docker-compose -f $SERVICES_COMPOSE down
        docker-compose -f $SERVICES_COMPOSE up -d
        echo "✅ Сервисы перезапущены"
        ;;
        
    status)
        echo "📊 Статус сервисов:"
        docker-compose -f $SERVICES_COMPOSE ps
        
        echo ""
        echo "🔍 Проверка подключений:"
        
        # PostgreSQL main
        if docker-compose -f $SERVICES_COMPOSE exec postgres pg_isready -U postgres >/dev/null 2>&1; then
            echo "✅ PostgreSQL (main) - доступен"
        else
            echo "❌ PostgreSQL (main) - недоступен"
        fi
        
        # PostgreSQL test
        if docker-compose -f $SERVICES_COMPOSE exec postgres_test pg_isready -U postgres >/dev/null 2>&1; then
            echo "✅ PostgreSQL (test) - доступен"
        else
            echo "❌ PostgreSQL (test) - недоступен"
        fi
        
        # Redis
        if docker-compose -f $SERVICES_COMPOSE exec redis redis-cli ping >/dev/null 2>&1; then
            echo "✅ Redis - доступен"
        else
            echo "❌ Redis - недоступен"
        fi
        ;;
        
    logs)
        echo "📋 Логи сервисов:"
        docker-compose -f $SERVICES_COMPOSE logs -f
        ;;
        
    clean)
        echo "🧹 Очистка данных сервисов..."
        docker-compose -f $SERVICES_COMPOSE down -v
        echo "✅ Данные очищены"
        ;;
        
    force-stop)
        echo "🛑 Принудительная остановка всех контейнеров проекта..."
        
        # Останавливаем через docker-compose
        docker-compose -f $SERVICES_COMPOSE down 2>/dev/null || true
        
        # Принудительно останавливаем контейнеры
        docker stop vk_parser_postgres vk_parser_postgres_test vk_parser_redis 2>/dev/null || true
        docker rm vk_parser_postgres vk_parser_postgres_test vk_parser_redis 2>/dev/null || true
        
        # Убиваем процессы на портах
        echo "🔪 Освобождение портов..."
        sudo pkill -f postgres 2>/dev/null || true
        sudo pkill -f redis 2>/dev/null || true
        
        # Проверяем что порты освободились
        sleep 3
        if netstat -tlnp 2>/dev/null | grep -E ":(5435|5434|6379) " >/dev/null; then
            echo "⚠️ Некоторые порты все еще заняты:"
            netstat -tlnp 2>/dev/null | grep -E ":(5435|5434|6379) " || true
        else
            echo "✅ Все порты освобождены"
        fi
        
        echo "✅ Все контейнеры остановлены"
        ;;
        
    *)
        echo "Управление сервисами PostgreSQL и Redis"
        echo ""
        echo "Использование: $0 {start|stop|restart|status|logs|clean|force-stop}"
        echo ""
        echo "Команды:"
        echo "  start      - Запустить сервисы"
        echo "  stop       - Остановить сервисы"
        echo "  restart    - Перезапустить сервисы"
        echo "  status     - Показать статус сервисов"
        echo "  logs       - Показать логи сервисов"
        echo "  clean      - Остановить и удалить данные"
        echo "  force-stop - Принудительно остановить все контейнеры"
        exit 1
        ;;
esac
