---
## Рефакторинг CI/CD

**План:**
1. Анализ и фиксация текущих workflow и версий actions
2. Обновление actions до последних стабильных версий
3. Вынесение общих шагов (линтинг, тесты, кэширование) в reusable workflows
4. Оптимизация кэширования (Poetry, pnpm, Docker layers)
5. Минимизация permissions для всех jobs
6. Добавление сканирования зависимостей (CodeQL, npm audit, poetry check)
7. Добавление уведомлений о статусе деплоя (Slack/Telegram, если есть webhooks)
8. Проверка и реализация параллелизма и fail-fast
9. Обновление документации по CI/CD (README.md, docs/CI_FIXES.md)
10. Проведение ревью и тестирования новых workflow

**Чеклист:**
- [x] Зафиксировать текущие workflow и их версии
- [x] Обновить actions до последних версий
- [x] Вынести общие шаги в reusable workflows
- [x] Оптимизировать кэширование
- [x] Минимизировать permissions
- [x] Добавить сканирование зависимостей
- [x] Добавить уведомления о деплое
- [x] Проверить параллелизм и fail-fast
- [x] Обновить документацию
- [x] Провести ревью и тестирование
- [x] Реализовать кэширование Docker-слоёв для локальных buildx-билдов (developer experience)

**Текущие workflow и actions:**

- **ci.yml**: основной pipeline, вызывает reusable workflows для backend и frontend
  - actions/checkout@v4
  - ./.github/workflows/reusable-backend-test.yml
  - ./.github/workflows/reusable-frontend-test.yml

- **reusable-backend-test.yml**:
  - actions/checkout@v4
  - actions/setup-python@v5
  - snok/install-poetry@v1
  - actions/cache@v4
  - codecov/codecov-action@v4
  - actions/upload-artifact@v4

- **reusable-frontend-test.yml**:
  - actions/checkout@v4
  - pnpm/action-setup@v4
  - actions/setup-node@v4
  - actions/upload-artifact@v4
  - codecov/codecov-action@v4

- **deploy-production.yml**:
  - actions/checkout@v4.1.1
  - docker/login-action@v3.1.0
  - docker/build-push-action@v5.3.0
  - appleboy/ssh-action@v0.1.10

- **deploy-staging.yml**:
  - actions/checkout@v4.1.1
  - appleboy/ssh-action@v0.1.10

- **security.yml**:
  - actions/checkout@v4.1.1
  - trufflesecurity/trufflehog@v3.67.3
  - github/codeql-action/init@v3
  - github/codeql-action/autobuild@v3
  - github/codeql-action/analyze@v3
  - docker/setup-buildx-action@v3
  - docker/build-push-action@v5.3.0
  - aquasecurity/trivy-action@v0.17.0
  - github/codeql-action/upload-sarif@v3

- **release.yml**:
  - actions/checkout@v4.1.1
  - actions/setup-python@v5
  - snok/install-poetry@v1
  - actions/cache@v4
  - pnpm/action-setup@v4
  - actions/setup-node@v4
  - docker/setup-buildx-action@v3
  - docker/login-action@v3.1.0
  - docker/metadata-action@v5
  - docker/build-push-action@v5.3.0
  - mikepenz/release-changelog-builder-action@v4
  - softprops/action-gh-release@v2
