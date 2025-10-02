import { Router, Application } from 'express';
import groupsRoutes from './groups.routes';
import healthRoutes from './health.routes';
import { responseFormatter, errorHandler, notFoundHandler } from '@presentation/middleware/responseFormatter';
import { requestContextMiddleware, initRequestContext } from '@presentation/middleware/requestContext';
import { securityHeaders, apiHeaders } from '@presentation/middleware/security';
import { initializeDIContainer } from '@infrastructure/di/initialization';

/**
 * Главный роутер API приложения
 *
 * Clean Architecture структура:
 * - /api/groups/*   - управление группами (Clean Architecture)
 * - /api/health/*   - health checks
 */

// === ИНИЦИАЛИЗАЦИЯ DI CONTAINER ===
// Инициализируем контейнер зависимостей при старте приложения
initializeDIContainer();

// === СОЗДАНИЕ API РОУТЕРА ===
const apiRouter = Router();

// === ПОДКЛЮЧЕНИЕ SUB-ROUTES ===

// Группы VK
apiRouter.use('/groups', groupsRoutes);

// Health checks
apiRouter.use('/health', healthRoutes);

// === ОБРАБОТЧИК 404 ДЛЯ API МАРШРУТОВ ===
// Применяется ко всем неопределенным маршрутам API
apiRouter.use(notFoundHandler);

/**
 * Настраивает маршруты и middleware для Express приложения
 * @param app Express приложение
 */
export const setupRoutes = (app: Application): void => {
  // Security заголовки (должны быть первыми)
  app.use(securityHeaders);

  // Request ID и контекст (должны быть ранними)
  app.use(requestContextMiddleware);
  app.use(initRequestContext);

  // API заголовки для всех API маршрутов
  app.use('/api', apiHeaders);

  // Применяем форматтер ответов ко всем API маршрутам
  app.use('/api', responseFormatter);

  // Подключаем API роутер
  app.use('/api', apiRouter);

  // Глобальный обработчик ошибок (должен быть последним)
  app.use(errorHandler);
};

// Экспорт роутера для использования в тестах
export default apiRouter;
