.PHONY: feature release hotfix cleanup sync

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