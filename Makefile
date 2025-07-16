.PHONY: feature release hotfix cleanup sync release-create release-deploy release-rollback

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