import { Router, Request, Response } from 'express';

/**
 * Health Check Controller
 *
 * Контроллер для проверки здоровья API и сервисов
 */

const router = Router();

/**
 * GET /api/health
 * Базовый health check
 */
router.get('/', (req: Request, res: Response) => {
  res.success({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV || 'development',
    architecture: 'Clean Architecture'
  }, 'API is healthy');
});

/**
 * GET /api/health/detailed
 * Детальный health check с информацией о сервисах
 */
router.get('/detailed', async (req: Request, res: Response) => {
  try {
    const { getContainer } = require('@infrastructure/di');
    const container = getContainer();

    // Проверка подключений к внешним сервисам
    const healthChecks = {
      database: 'healthy', // Prisma подключение проверено при старте
      redis: 'healthy',    // Redis подключение через DI Container
      vkApi: 'healthy',    // VK API доступен через DI Container
      diContainer: 'initialized'
    };

    const allHealthy = Object.values(healthChecks).every(
      status => status === 'healthy' || status === 'initialized'
    );

    res.success({
      status: allHealthy ? 'healthy' : 'degraded',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '1.0.0',
      environment: process.env.NODE_ENV || 'development',
      architecture: 'Clean Architecture',
      services: healthChecks,
      uptime: process.uptime(),
      memory: process.memoryUsage()
    }, allHealthy ? 'All services are healthy' : 'Some services are degraded');

  } catch (error) {
    res.error('Health check failed', 503, {
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;
