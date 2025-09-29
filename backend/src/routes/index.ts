import { Router } from 'express';
import taskController from '@/controllers/taskController';
import vkCollectController from '@/controllers/vkCollectController';
import taskResultsController from '@/controllers/taskResultsController';
import groupsController from '@/controllers/groupsController';
import groupsStatsController from '@/controllers/groupsStatsController';
import { responseFormatter, errorHandler, notFoundHandler } from '@/middleware/responseFormatter';

// Создаем главный роутер для API
const apiRouter = Router();

/**
 * Централизованная настройка маршрутов API
 *
 * Структура маршрутов:
 * - /api/tasks/*           - базовые операции с задачами
 * - /api/vk/*              - VK специфичные операции
 * - /api/results/*         - получение результатов задач
 * - /api/groups/*          - операции с группами
 * - /api/stats/*           - статистические операции
 */

// === БАЗОВЫЕ ОПЕРАЦИИ С ЗАДАЧАМИ ===
// POST /api/tasks - создание задач
// GET /api/tasks/:taskId - получение задачи
// GET /api/tasks - список задач
apiRouter.use('/api', taskController);

// === VK КОЛЛЕКЦИЯ ОПЕРАЦИИ ===
// POST /api/vk/collect - создание задачи VK коллекции
// POST /api/vk/collect/:taskId/start - запуск сбора
apiRouter.use('/api', vkCollectController);

// === РЕЗУЛЬТАТЫ ЗАДАЧ ===
// GET /api/results/:taskId - получение результатов
// GET /api/results/:taskId/summary - сводка результатов
// GET /api/results/:taskId/export - экспорт результатов
apiRouter.use('/api', taskResultsController);

// === ОПЕРАЦИИ С ГРУППАМИ ===
// POST /api/groups/upload - загрузка групп
// GET /api/groups - список групп
// DELETE /api/groups/:groupId - удаление группы
// DELETE /api/groups/batch - массовое удаление
apiRouter.use('/api', groupsController);

// === СТАТИСТИЧЕСКИЕ ОПЕРАЦИИ ===
// GET /api/stats/groups - общая статистика групп
// GET /api/stats/groups/:taskId - статистика по задаче
// GET /api/stats/groups/summary - сводная статистика
// GET /api/stats/groups/activity - активность групп
apiRouter.use('/api', groupsStatsController);

// === ЗДОРОВЬЕ API ===
// Базовый health check
apiRouter.get('/api/health', (req, res) => {
  res.success({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV || 'development'
  }, 'API is healthy');
});

// Детальный health check
apiRouter.get('/api/health/detailed', async (req, res) => {
  try {
    // Проверка подключений к внешним сервисам
    const healthChecks = {
      database: 'healthy', // TODO: добавить проверку БД
      redis: 'healthy',    // TODO: добавить проверку Redis
      vkApi: 'healthy'     // TODO: добавить проверку VK API
    };

    const allHealthy = Object.values(healthChecks).every(status => status === 'healthy');

    res.success({
      status: allHealthy ? 'healthy' : 'degraded',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '1.0.0',
      environment: process.env.NODE_ENV || 'development',
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

// === ОБРАБОТЧИК 404 ДЛЯ API МАРШРУТОВ ===
// Применяется только к маршрутам начинающимся с /api/
apiRouter.use('/api/*', notFoundHandler);

/**
 * Создает и настраивает главный роутер приложения
 * @param app Express приложение
 */
export const setupRoutes = (app: any) => {
  // Применяем форматтер ответов ко всем API маршрутам
  app.use('/api', responseFormatter);

  // Регистрируем все API маршруты
  app.use(apiRouter);

  // Глобальный обработчик ошибок (должен быть последним)
  app.use(errorHandler);
};

// Экспорт роутера для использования в тестах или отдельных модулях
export default apiRouter;

// Экспорт отдельных контроллеров для использования в других местах
export {
  taskController,
  vkCollectController,
  taskResultsController,
  groupsController,
  groupsStatsController
};