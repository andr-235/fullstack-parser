# =============================================================================
# Optimized Makefile for Docker Operations
# =============================================================================

.PHONY: help build build-prod build-dev up up-prod up-dev down down-prod down-dev \
        logs logs-prod logs-dev clean clean-all prune prune-all \
        restart restart-prod restart-dev status status-prod status-dev \
        health health-prod health-dev backup backup-prod \
        optimize-images scan-vulnerabilities monitor-resources \
        pgadmin pgadmin-start pgadmin-stop pgadmin-logs pgadmin-restart \
        db-exec db-backup db-restore db-status db-tables db-connect \
        update-authors check-authors backend-exec backend-shell

# Переменные
COMPOSE_PROD = docker-compose.prod.ip.yml
COMPOSE_DEV = docker-compose.dev.yml
COMPOSE_PROD_IP = docker-compose.prod.ip.yml

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Показать справку
	@echo "$(GREEN)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# Сборка образов
# =============================================================================

build: ## Собрать все образы для разработки
	@echo "$(GREEN)Сборка образов для разработки...$(NC)"
	docker-compose -f $(COMPOSE_DEV) build --parallel --no-cache

build-prod: ## Собрать все образы для продакшена
	@echo "$(GREEN)Сборка образов для продакшена...$(NC)"
	DOCKER_BUILDKIT=1 docker-compose -f $(COMPOSE_PROD) build --parallel --no-cache

build-dev: ## Собрать образы для разработки с кешированием
	@echo "$(GREEN)Сборка образов для разработки с кешированием...$(NC)"
	DOCKER_BUILDKIT=1 docker-compose -f $(COMPOSE_DEV) build --parallel

# =============================================================================
# Запуск и остановка
# =============================================================================

up: ## Запустить все сервисы для разработки
	@echo "$(GREEN)Запуск сервисов для разработки...$(NC)"
	docker-compose -f $(COMPOSE_DEV) up -d

up-prod: ## Запустить все сервисы для продакшена
	@echo "$(GREEN)Запуск сервисов для продакшена...$(NC)"
	docker-compose -f $(COMPOSE_PROD) up -d

up-dev: ## Запустить сервисы для разработки с логами
	@echo "$(GREEN)Запуск сервисов для разработки с логами...$(NC)"
	docker-compose -f $(COMPOSE_DEV) up

down: ## Остановить все сервисы разработки
	@echo "$(YELLOW)Остановка сервисов разработки...$(NC)"
	docker-compose -f $(COMPOSE_DEV) down

down-prod: ## Остановить все сервисы продакшена
	@echo "$(YELLOW)Остановка сервисов продакшена...$(NC)"
	docker-compose -f $(COMPOSE_PROD) down

down-dev: ## Остановить сервисы разработки с удалением томов
	@echo "$(YELLOW)Остановка сервисов разработки с удалением томов...$(NC)"
	docker-compose -f $(COMPOSE_DEV) down -v

# =============================================================================
# Логи и мониторинг
# =============================================================================

logs: ## Показать логи разработки
	docker-compose -f $(COMPOSE_DEV) logs -f --tail=100

logs-prod: ## Показать логи продакшена
	docker-compose -f $(COMPOSE_PROD) logs -f --tail=100

logs-dev: ## Показать логи конкретного сервиса разработки
	@read -p "Введите имя сервиса: " service; \
	docker-compose -f $(COMPOSE_DEV) logs -f --tail=100 $$service

# =============================================================================
# Управление состоянием
# =============================================================================

restart: ## Перезапустить сервисы разработки
	@echo "$(GREEN)Перезапуск сервисов разработки...$(NC)"
	docker-compose -f $(COMPOSE_DEV) restart

restart-prod: ## Перезапустить сервисы продакшена
	@echo "$(GREEN)Перезапуск сервисов продакшена...$(NC)"
	docker-compose -f $(COMPOSE_PROD) restart

restart-dev: ## Перезапустить конкретный сервис разработки
	@read -p "Введите имя сервиса: " service; \
	docker-compose -f $(COMPOSE_DEV) restart $$service

status: ## Показать статус сервисов разработки
	@echo "$(GREEN)Статус сервисов разработки:$(NC)"
	docker-compose -f $(COMPOSE_DEV) ps

status-prod: ## Показать статус сервисов продакшена
	@echo "$(GREEN)Статус сервисов продакшена:$(NC)"
	docker-compose -f $(COMPOSE_PROD) ps

status-dev: ## Показать детальный статус сервисов разработки
	@echo "$(GREEN)Детальный статус сервисов разработки:$(NC)"
	docker-compose -f $(COMPOSE_DEV) ps -a

# =============================================================================
# Проверка здоровья
# =============================================================================

health: ## Проверить здоровье сервисов разработки
	@echo "$(GREEN)Проверка здоровья сервисов разработки:$(NC)"
	@for service in $$(docker-compose -f $(COMPOSE_DEV) ps -q); do \
		echo "Проверка $$(docker inspect --format='{{.Name}}' $$service):"; \
		docker inspect --format='{{.State.Health.Status}}' $$service; \
	done

health-prod: ## Проверить здоровье сервисов продакшена
	@echo "$(GREEN)Проверка здоровья сервисов продакшена:$(NC)"
	@for service in $$(docker-compose -f $(COMPOSE_PROD) ps -q); do \
		echo "Проверка $$(docker inspect --format='{{.Name}}' $$service):"; \
		docker inspect --format='{{.State.Health.Status}}' $$service; \
	done

health-dev: ## Проверить здоровье конкретного сервиса
	@read -p "Введите имя сервиса: " service; \
	echo "$(GREEN)Проверка здоровья сервиса $$service:$(NC)"; \
	docker-compose -f $(COMPOSE_DEV) exec $$service curl -f http://localhost:8000/api/v1/health/ || echo "$(RED)Сервис недоступен$(NC)"

# =============================================================================
# Очистка и оптимизация
# =============================================================================

clean: ## Очистить неиспользуемые образы и контейнеры
	@echo "$(YELLOW)Очистка неиспользуемых образов и контейнеров...$(NC)"
	docker system prune -f

clean-all: ## Полная очистка Docker (внимание!)
	@echo "$(RED)ВНИМАНИЕ: Полная очистка Docker!$(NC)"
	@read -p "Вы уверены? (y/N): " confirm; \
	if [ "$$confirm" = "y" ]; then \
		docker system prune -a -f --volumes; \
	else \
		echo "Операция отменена"; \
	fi

prune: ## Удалить неиспользуемые тома
	@echo "$(YELLOW)Удаление неиспользуемых томов...$(NC)"
	docker volume prune -f

prune-all: ## Удалить все тома (внимание!)
	@echo "$(RED)ВНИМАНИЕ: Удаление всех томов!$(NC)"
	@read -p "Вы уверены? (y/N): " confirm; \
	if [ "$$confirm" = "y" ]; then \
		docker volume prune -a -f; \
	else \
		echo "Операция отменена"; \
	fi

# =============================================================================
# Оптимизация и безопасность
# =============================================================================

optimize-images: ## Оптимизировать размеры образов
	@echo "$(GREEN)Оптимизация размеров образов...$(NC)"
	@echo "Анализ размеров образов:"
	docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
	@echo ""
	@echo "Рекомендации по оптимизации:"
	@echo "1. Используйте multi-stage builds"
	@echo "2. Объединяйте RUN команды"
	@echo "3. Удаляйте кеш пакетных менеджеров"
	@echo "4. Используйте .dockerignore"

scan-vulnerabilities: ## Сканировать образы на уязвимости
	@echo "$(GREEN)Сканирование образов на уязвимости...$(NC)"
	@for image in $$(docker images --format "{{.Repository}}:{{.Tag}}" | grep -v "<none>"); do \
		echo "Сканирование $$image..."; \
		docker scout cves $$image || echo "Docker Scout недоступен"; \
	done

monitor-resources: ## Мониторинг использования ресурсов
	@echo "$(GREEN)Мониторинг использования ресурсов:$(NC)"
	@echo "Использование CPU и памяти:"
	docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
	@echo ""
	@echo "Использование диска:"
	docker system df

# =============================================================================
# Резервное копирование
# =============================================================================

backup: ## Создать резервную копию данных разработки
	@echo "$(GREEN)Создание резервной копии данных разработки...$(NC)"
	@mkdir -p backup/$(shell date +%Y%m%d_%H%M%S)
	@docker-compose -f $(COMPOSE_DEV) exec -T db pg_dump -U postgres fullstack_dev > backup/$(shell date +%Y%m%d_%H%M%S)/db_backup.sql
	@echo "Резервная копия создана в backup/$(shell date +%Y%m%d_%H%M%S)/"

backup-prod: ## Создать резервную копию данных продакшена
	@echo "$(GREEN)Создание резервной копии данных продакшена...$(NC)"
	@mkdir -p backup/prod/$(shell date +%Y%m%d_%H%M%S)
	@docker-compose -f $(COMPOSE_PROD) exec -T postgres pg_dump -U ${DB_USER} ${DB_NAME} > backup/prod/$(shell date +%Y%m%d_%H%M%S)/db_backup.sql
	@echo "Резервная копия продакшена создана в backup/prod/$(shell date +%Y%m%d_%H%M%S)/"

# =============================================================================
# Быстрые команды
# =============================================================================

dev: build-dev up ## Быстрый запуск разработки (сборка + запуск)
	@echo "$(GREEN)Разработка запущена!$(NC)"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "pgAdmin: http://localhost:5050"
	@echo "MailHog: http://localhost:8025"
	@echo "Redis Commander: http://localhost:8081"

prod: build-prod up-prod ## Быстрый запуск продакшена (сборка + запуск)
	@echo "$(GREEN)Продакшен запущен!$(NC)"

stop: down ## Быстрая остановка разработки
	@echo "$(YELLOW)Разработка остановлена$(NC)"

stop-prod: down-prod ## Быстрая остановка продакшена
	@echo "$(YELLOW)Продакшен остановлен$(NC)"

# =============================================================================
# pgAdmin команды
# =============================================================================

pgadmin: pgadmin-start ## Быстрый запуск pgAdmin

pgadmin-start: ## Запустить pgAdmin для управления БД
	@echo "$(GREEN)Запуск pgAdmin...$(NC)"
	docker-compose -f $(COMPOSE_PROD_IP) --profile admin up pgadmin -d
	@echo "$(GREEN)pgAdmin запущен!$(NC)"
	@echo "Доступ: http://localhost:5050"
	@echo "Email: admin@admin.com"
	@echo "Пароль: admin"
	@echo "Сервер: postgres"
	@echo "Пользователь: ${DB_USER}"
	@echo "База данных: ${DB_NAME}"

pgadmin-stop: ## Остановить pgAdmin
	@echo "$(YELLOW)Остановка pgAdmin...$(NC)"
	docker-compose -f $(COMPOSE_PROD_IP) stop pgadmin
	@echo "$(YELLOW)pgAdmin остановлен$(NC)"

pgadmin-logs: ## Показать логи pgAdmin
	@echo "$(GREEN)Логи pgAdmin:$(NC)"
	docker-compose -f $(COMPOSE_PROD_IP) logs -f pgadmin

pgadmin-restart: ## Перезапустить pgAdmin
	@echo "$(GREEN)Перезапуск pgAdmin...$(NC)"
	docker-compose -f $(COMPOSE_PROD_IP) restart pgadmin
	@echo "$(GREEN)pgAdmin перезапущен$(NC)"

# =============================================================================
# Команды для работы с БД
# =============================================================================

db-exec: ## Выполнить SQL запрос в БД
	@read -p "Введите SQL запрос: " query; \
	docker-compose -f $(COMPOSE_PROD_IP) exec -T postgres psql -U ${DB_USER} -d ${DB_NAME} -c "$$query"

db-backup: ## Создать резервную копию БД
	@echo "$(GREEN)Создание резервной копии БД...$(NC)"
	@mkdir -p backup/$(shell date +%Y%m%d_%H%M%S)
	docker-compose -f $(COMPOSE_PROD_IP) exec -T postgres pg_dump -U ${DB_USER} ${DB_NAME} > backup/$(shell date +%Y%m%d_%H%M%S)/db_backup.sql
	@echo "Резервная копия создана в backup/$(shell date +%Y%m%d_%H%M%S)/"

db-restore: ## Восстановить БД из резервной копии
	@echo "$(YELLOW)ВНИМАНИЕ: Восстановление БД из резервной копии!$(NC)"
	@read -p "Введите путь к файлу резервной копии: " file; \
	if [ -f "$$file" ]; then \
		docker-compose -f $(COMPOSE_PROD_IP) exec -T postgres psql -U ${DB_USER} -d ${DB_NAME} < $$file; \
		echo "$(GREEN)БД восстановлена из $$file$(NC)"; \
	else \
		echo "$(RED)Файл $$file не найден$(NC)"; \
	fi

db-status: ## Показать статус БД
	@echo "$(GREEN)Статус БД:$(NC)"
	docker-compose -f $(COMPOSE_PROD_IP) exec -T postgres psql -U ${DB_USER} -d ${DB_NAME} -c "SELECT version();"
	@echo ""
	@echo "$(GREEN)Размер БД:$(NC)"
	docker-compose -f $(COMPOSE_PROD_IP) exec -T postgres psql -U ${DB_USER} -d ${DB_NAME} -c "SELECT pg_size_pretty(pg_database_size('${DB_NAME}'));"

db-tables: ## Показать список таблиц
	@echo "$(GREEN)Список таблиц в БД:$(NC)"
	docker-compose -f $(COMPOSE_PROD_IP) exec -T postgres psql -U ${DB_USER} -d ${DB_NAME} -c "\dt"

db-connect: ## Подключиться к БД через psql
	@echo "$(GREEN)Подключение к БД...$(NC)"
	docker-compose -f $(COMPOSE_PROD_IP) exec postgres psql -U ${DB_USER} -d ${DB_NAME}

# =============================================================================
# Команды для работы со скриптами
# =============================================================================

update-authors: ## Обновить данные авторов в БД
	@echo "$(GREEN)Обновление данных авторов в БД...$(NC)"
	@if [ -f "backend/update_all_authors.py" ]; then \
		docker cp backend/update_all_authors.py fullstack_prod_backend:/app/update_all_authors.py; \
		docker-compose -f $(COMPOSE_PROD_IP) exec backend python update_all_authors.py; \
		docker-compose -f $(COMPOSE_PROD_IP) exec backend rm -f update_all_authors.py; \
	else \
		echo "$(RED)Файл backend/update_all_authors.py не найден$(NC)"; \
	fi

check-authors: ## Проверить данные авторов в БД
	@echo "$(GREEN)Проверка данных авторов в БД...$(NC)"
	@if [ -f "backend/check_authors.py" ]; then \
		docker cp backend/check_authors.py fullstack_prod_backend:/app/check_authors.py; \
		docker-compose -f $(COMPOSE_PROD_IP) exec backend python check_authors.py; \
		docker-compose -f $(COMPOSE_PROD_IP) exec backend rm -f check_authors.py; \
	else \
		echo "$(RED)Файл backend/check_authors.py не найден$(NC)"; \
	fi

backend-exec: ## Выполнить команду в backend контейнере
	@read -p "Введите команду для выполнения в backend: " cmd; \
	docker-compose -f $(COMPOSE_PROD_IP) exec backend $$cmd

backend-shell: ## Открыть shell в backend контейнере
	@echo "$(GREEN)Открытие shell в backend контейнере...$(NC)"
	docker-compose -f $(COMPOSE_PROD_IP) exec backend bash 