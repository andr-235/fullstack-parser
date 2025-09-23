## Реализация VK API интеграции по ТЗ

**Last performed:** 2025-09-23

**Files to modify:**
- `backend/src/models/*.js` - data schemas (comment.js, post.js, task.js)
- `backend/src/repositories/*.js` - data access (dbRepo.js для PostgreSQL, vkApi.js для VK API calls)
- `backend/src/services/*.js` - business logic (taskService.js для async tasks, vkService.js для VK integration)
- `backend/src/controllers/*.js` - HTTP handlers (taskController.js для /api/tasks)
- `backend/package.json` - добавь зависимости: axios, rate-limiter-flexible

**Steps:**
1. [x] Создай models (Comment, Post, Task) - реализованы в comment.js, post.js, task.js.
2. [x] Реализуй repositories с HTTP client и rate limiting - vkApi.js с axios, rate limiter (3 req/s), getComments/getPosts/renewToken, retry.
3. [x] Создай services (vkService, taskService) - vkService.js (Redis tokens), taskService.js (placeholders для BullMQ).
4. [x] Добавь controllers и routes для /api/tasks - taskController.js (fetchComments, taskStatus), routes в server.js.
5. [ ] Настрой BullMQ tasks (vk:fetch_comments, morphological:analyze).
6. [ ] Интегрируй морфологический анализ.
7. [ ] Напиши тесты (>80% покрытие).

**Important notes:**
- Соблюдай MVC-like структуру, rate limits VK (3 req/s), retry с backoff, env для токенов.
- Тестируй с mocks (jest.mock). Обнови context.md после.
- Progress: Steps 1-4 реализованы частично (placeholders в services), 5-7 pending.

**Example of the completed implementation:**
```javascript
// backend/src/repositories/vkApi.js

const axios = require('axios');
const { RateLimiterMemory } = require('rate-limiter-flexible');
const logger = require('../utils/logger');

const limiter = new RateLimiterMemory({
  points: 3, // 3 req/s
  duration: 1, // per second
});

class VKApi {
  constructor() {
    this.baseURL = 'https://api.vk.com/method';
    this.version = '5.131';
  }

  async getComments(ownerId, postId, token) {
    await limiter.consume('vk-api'); // rate limit

    try {
      const response = await axios.get(`${this.baseURL}/wall.getComments`, {
        params: {
          owner_id: ownerId,
          post_id: postId,
          access_token: token,
          v: this.version,
        },
      });

      if (response.data.error) {
        throw new Error(`VK API error: ${response.data.error.error_msg}`);
      }

      return response.data.response.items;
    } catch (error) {
      logger.error('VK API request failed:', error.message);
      throw error;
    }
  }
}

module.exports = new VKApi();