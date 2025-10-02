import { Router } from 'express';
import groupsController from '@presentation/http/controllers/GroupsController';

/**
 * Groups Routes
 *
 * Маршруты для управления группами VK
 *
 * Endpoints:
 * - POST   /api/groups/upload - загрузка групп из файла
 * - GET    /api/groups        - список групп с фильтрацией и пагинацией
 * - GET    /api/groups/stats  - статистика по группам
 * - DELETE /api/groups/:id    - удаление группы по ID
 * - DELETE /api/groups        - массовое удаление групп
 */

const router = Router();

// Подключаем все маршруты групп через контроллер
router.use('/', groupsController);

export default router;
