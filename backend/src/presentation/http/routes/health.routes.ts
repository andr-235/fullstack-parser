import { Router } from 'express';
import healthController from '@presentation/http/controllers/HealthController';

/**
 * Health Check Routes
 *
 * Маршруты для проверки здоровья API и сервисов
 *
 * Endpoints:
 * - GET /api/health          - базовый health check
 * - GET /api/health/detailed - детальный health check с метриками
 */

const router = Router();

// Подключаем health check контроллер
router.use('/', healthController);

export default router;
