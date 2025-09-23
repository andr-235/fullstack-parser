# Tech

## Technologies used
- **Backend**: Node.js (с Bun для package management), Express (web framework), pg или Sequelize (ORM для PostgreSQL), redis (client для Redis), axios или node-fetch (HTTP client для VK API).
- **Database**: PostgreSQL (persistent storage), Redis (cache, tokens, queues).
- **Frontend**: Vue.js 3 (UI framework), Pinia (state management), Vue Router (navigation), Vite (build tool).
- **Testing**: Jest (unit/integration для backend), Vitest (для frontend).
- **Other**: Docker (containerization), .env (configuration), Bun lock для dependencies.

## Development setup
- **Build**: bun install (или npm install) в backend/ и frontend/, bun build или tsc если TS.
- **Run**: docker-compose up (PostgreSQL, Redis, backend, frontend; env_file .env, ports 5432, 6379, 3000 для backend, 8080 для frontend); node backend/server.js (API на :3000), bun run dev в frontend/ (Vite dev server).
- **Testing**: bun test (Jest в backend/), bun test (Vitest в frontend/), coverage с nyc или встроенным.
- **Deployment**: Docker images для backend/frontend, nginx.conf для serving frontend, PM2 или Docker Swarm для scaling.

## Technical constraints
- **VK API**: Rate limit 3 req/s, 5000 calls/day; retry with exponential backoff в vkApi.js.
- **Performance**: Async/await для scalability, taskService.js для background tasks (возможно BullMQ с Redis).
- **Security**: Env vars for secrets (DB_URL, VK_TOKEN), CORS в Express, input validation (express-validator), no hard-coded tokens.
- **Language**: JavaScript/ES6+ для backend/frontend, миграция с Python для consistency.

## Dependencies
- express (API routing)
- pg или sequelize (DB ORM)
- redis (Redis client)
- axios (HTTP для VK)
- bullmq или подобное (queues, если используется)
- vue, pinia, vue-router (frontend)
- vite (build)
- jest, vitest (tests)
- dotenv (env vars)

## Tool usage patterns
- **Testing**: TDD, >80% coverage, unit (mocks с jest.mock), integration (supertest для API).
- **CI/CD**: GitHub Actions для build/test/deploy.
- **Monitoring**: Express middleware для logging (logger.js), возможно Winston для structured logs.
- **Code quality**: ESLint/Prettier (frontend eslint.config.js, .prettierrc), Husky hooks для pre-commit.