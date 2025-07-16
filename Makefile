.PHONY: feature release hotfix cleanup sync release-create release-deploy release-rollback dev test build deploy status logs clean branch commit push pr

# 🚀 Упрощённые команды для одного разработчика
dev: ## Запуск в режиме разработки
	@echo "🚀 Запуск в режиме разработки..."
	docker compose up -d
	@echo "✅ Сервисы запущены! Frontend: http://localhost:3000, Backend: http://localhost:8000"

test: ## Быстрые тесты
	@echo "🧪 Запуск быстрых тестов..."
	@cd backend && poetry run pytest tests/ -v --tb=short --maxfail=3
	@cd frontend && pnpm test --passWithNoTests --watchAll=false
	@echo "✅ Тесты пройдены!"

build: ## Сборка образов
	@echo "🏗️ Сборка Docker образов..."
	docker compose build
	@echo "✅ Образы собраны!"

deploy: ## Деплой в production
	@echo "🚀 Деплой в production..."
	@read -p "Ты уверен? Это задеплоит в production! (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		git push origin main; \
		echo "✅ Деплой запущен! Следи за CI/CD pipeline"; \
	else \
		echo "❌ Деплой отменён"; \
	fi

status: ## Статус сервисов
	@echo "📊 Статус сервисов:"
	docker compose ps
	@echo ""
	@echo "🔍 Логи последних ошибок:"
	docker compose logs --tail=10 --no-color | grep -i error || echo "Ошибок не найдено"

logs: ## Показать логи
	@echo "📝 Логи сервисов:"
	docker compose logs -f

clean: ## Очистка
	@echo "🧹 Очистка Docker..."
	docker compose down
	docker system prune -f
	docker image prune -f
	@echo "✅ Очистка завершена!"

# 🔧 Git команды
branch: ## Создать новую ветку
	@read -p "Название ветки (без feature/): " name; \
	git checkout -b feature/$$name
	@echo "✅ Создана ветка feature/$$name"

commit: ## Коммит изменений
	@read -p "Тип коммита (feat/fix/docs/style/refactor/test/chore): " type; \
	read -p "Описание: " desc; \
	git add . && git commit -m "$$type: $$desc"
	@echo "✅ Коммит создан!"

push: ## Пуш в репозиторий
	@git push origin HEAD
	@echo "✅ Код отправлен в репозиторий!"

pr: ## Создать Pull Request
	@echo "🔗 Создание Pull Request..."
	@gh pr create --fill
	@echo "✅ Pull Request создан!"



# 🎯 Классические команды для команды
feature:
	@read -p "Feature name: " name; \
	git checkout develop && \
	git pull origin develop && \
	git checkout -b feature/$$name && \
	echo "✅ Created feature/$$name from develop"

release:
	@read -p "Version (e.g., 1.1.0): " version; \
	git checkout develop && \
	git pull origin develop && \
	git checkout -b release/v$$version && \
	echo "✅ Created release/v$$version from develop"

hotfix:
	@read -p "Hotfix name: " name; \
	git checkout main && \
	git pull origin main && \
	git checkout -b hotfix/$$name && \
	echo "✅ Created hotfix/$$name from main"

cleanup:
	@git branch --merged | grep -v "\*\|main\|develop" | xargs -n 1 git branch -d
	@git remote prune origin
	@echo "✅ Cleaned up merged branches"

sync:
	@git checkout main && git pull origin main
	@git checkout develop && git pull origin develop
	@echo "✅ Synced main and develop"

# 🚀 Release commands
release-create:
	@echo "🚀 Creating new release..."
	@./scripts/create-release.sh

release-deploy:
	@read -p "Version to deploy (e.g., 1.2.3): " version; \
	echo "🚀 Deploying version $$version..."; \
	docker-compose -f docker-compose.prod.ip.yml pull && \
	docker-compose -f docker-compose.prod.ip.yml up -d --build

release-rollback:
	@echo "🔄 Rolling back release..."
	@./scripts/rollback-release.sh

release-status:
	@echo "📊 Current release status:"; \
	echo "Backend version: $$(grep '^version = ' backend/pyproject.toml | sed 's/version = "\(.*\)"/\1/')"; \
	echo "Frontend version: $$(grep '"version":' frontend/package.json | sed 's/.*"version": "\(.*\)".*/\1/')"; \
	echo "Latest tag: $$(git describe --tags --abbrev=0 2>/dev/null || echo 'No tags found')"

# 📋 Справка
help: ## Показать справку
	@echo "🚀 Fullstack Parser - Makefile команды"
	@echo ""
	@echo "🎯 Упрощённые команды (один разработчик):"
	@echo "  make dev          - Запуск в режиме разработки"
	@echo "  make test         - Быстрые тесты"
	@echo "  make build        - Сборка образов"
	@echo "  make deploy       - Деплой в production"
	@echo "  make status       - Статус сервисов"
	@echo "  make logs         - Показать логи"
	@echo "  make clean        - Очистка Docker"
	@echo ""
	@echo "🔧 Git команды:"
	@echo "  make branch       - Создать новую ветку"
	@echo "  make commit       - Коммит изменений"
	@echo "  make push         - Пуш в репозиторий"
	@echo "  make pr           - Создать Pull Request"

	@echo ""
	@echo "🎯 Классические команды (команда):"
	@echo "  make feature      - Создать feature ветку"
	@echo "  make release      - Создать release ветку"
	@echo "  make hotfix       - Создать hotfix ветку"
	@echo "  make cleanup      - Очистка веток"
	@echo "  make sync         - Синхронизация main/develop"
	@echo ""
	@echo "📖 Документация:"
	@echo "  docs/SINGLE_DEV_CICD.md - Упрощённый CI/CD"
	@echo "  README.md - Основная документация" 