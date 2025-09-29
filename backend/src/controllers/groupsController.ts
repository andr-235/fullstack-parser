import express, { Request, Response } from 'express';
import { uploadSingle, handleUploadError, validateUploadedFile, logFileUpload } from '@/middleware/upload';
import groupsService from '@/services/groupsService';
import logger from '@/utils/logger';
import { ApiResponse, PaginationParams, ErrorCodes } from '@/types/express';
import { GetGroupsParams } from '@/services/groupsService';
import {
  GroupsUploadResponse,
  GroupsListResponse,
  GroupsStatsResponse
} from '@/types/api';

const router = express.Router();

interface UploadQuery {
  encoding?: BufferEncoding;
}

interface GetGroupsQuery extends PaginationParams {
  status?: string;
  search?: string;
  sortBy?: string;
  sortOrder?: 'ASC' | 'DESC' | 'asc' | 'desc';
}

interface BatchDeleteBody {
  groupIds: number[];
}

/**
 * POST /api/groups/upload
 * Загрузка файла с группами
 */
router.post('/upload',
  logFileUpload,
  uploadSingle,
  handleUploadError,
  validateUploadedFile,
  async (req: Request<{}, ApiResponse, {}, UploadQuery>, res: Response): Promise<void> => {
    try {
      if (!req.file) {
        res.error('Файл не был загружен', 400);
        return;
      }

      logger.info('Groups upload started', {
        filename: req.file.originalname,
        size: req.file.size,
        mimetype: req.file.mimetype
      });

      const encoding: BufferEncoding = (req.query.encoding as BufferEncoding) || 'utf-8';
      logger.info('Processing file with groupsService', { encoding });

      const result = await groupsService.uploadGroups(req.file.buffer, encoding);

      if (result.success) {
        logger.info('Groups upload successful', {
          taskId: result.data?.taskId,
          totalGroups: result.data?.totalGroups || 0
        });
        res.success(result.data, 'Файл с группами успешно загружен');
      } else {
        logger.info('Groups upload failed', { error: result.error, message: result.message });
        res.error(result.message || 'Ошибка обработки файла', 400);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Upload groups controller error', {
        filename: req.file?.originalname,
        error: errorMsg
      });
      res.error('Ошибка загрузки файла', 500, {
        filename: req.file?.originalname,
        originalError: errorMsg
      });
    }
  }
);

/**
 * GET /api/groups/upload/:taskId/status
 * Получение статуса загрузки
 */
router.get('/upload/:taskId/status', async (req: Request<{ taskId: string }>, res: Response): Promise<void> => {
  try {
    const { taskId } = req.params;
    const result = groupsService.getUploadStatus(taskId);

    if (result.success) {
      res.success(result.data, 'Статус загрузки получен');
    } else {
      res.error('Задача загрузки не найдена', 404, {
        taskId
      });
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get upload status controller error', {
      taskId: req.params.taskId,
      error: errorMsg
    });
    res.error('Ошибка получения статуса загрузки', 500, {
      taskId: req.params.taskId,
      originalError: errorMsg
    });
  }
});

/**
 * GET /api/groups
 * Получение списка групп
 */
router.get('/', async (req: Request<{}, ApiResponse, {}, GetGroupsQuery>, res: Response): Promise<void> => {
  try {
    const {
      page = 1,
      limit = 20,
      status = 'all',
      search = '',
      sortBy = 'uploadedAt',
      sortOrder = 'desc'
    } = req.query;

    // Валидация параметров
    const pageNum = Number(page);
    const limitNum = Number(limit);

    if (isNaN(pageNum) || pageNum < 1) {
      res.error('Номер страницы должен быть положительным числом', 400, {
        field: 'page',
        value: page,
        constraint: 'positive integer'
      });
      return;
    }

    if (isNaN(limitNum) || limitNum < 1 || limitNum > 10000) {
      res.error('Лимит должен быть от 1 до 10000', 400, {
        field: 'limit',
        value: limit,
        constraint: '1 <= limit <= 10000'
      });
      return;
    }

    const offset = (pageNum - 1) * limitNum;
    const params: GetGroupsParams = {
      limit: limitNum,
      offset,
      status: status !== 'all' ? status : undefined,
      search: search || undefined,
      sortBy,
      sortOrder
    };

    const result = await groupsService.getGroups(params);

    if (result.success) {
      // Используем пагинированный ответ для списка групп
      const pagination = {
        page: pageNum,
        limit: limitNum,
        total: result.data?.total || 0,
        totalPages: Math.ceil((result.data?.total || 0) / limitNum),
        hasNext: pageNum * limitNum < (result.data?.total || 0),
        hasPrev: pageNum > 1
      };

      res.paginated(result.data?.groups || [], pagination);
    } else {
      res.error(result.message || 'Ошибка получения списка групп', 500);
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get groups controller error', {
      query: req.query,
      error: errorMsg
    });
    res.error('Ошибка получения списка групп', 500, {
      query: req.query,
      originalError: errorMsg
    });
  }
});

/**
 * DELETE /api/groups/:groupId
 * Удаление группы
 */
router.delete('/:groupId', async (req: Request<{ groupId: string }>, res: Response): Promise<void> => {
  try {
    const { groupId } = req.params;

    // Валидация ID
    const groupIdNum = Number(groupId);
    if (isNaN(groupIdNum) || groupIdNum <= 0) {
      res.error('ID группы должен быть положительным числом', 400, {
        field: 'groupId',
        value: groupId,
        constraint: 'positive number'
      });
      return;
    }

    const result = await groupsService.deleteGroup(groupId);

    if (result.success) {
      res.success(result.data, 'Группа успешно удалена');
    } else {
      const errorCode = result.error === 'GROUP_NOT_FOUND' ? ErrorCodes.NOT_FOUND : ErrorCodes.INTERNAL_ERROR;
      const statusCode = result.error === 'GROUP_NOT_FOUND' ? 404 : 400;
      res.error(result.message || 'Ошибка удаления группы', statusCode, { groupId });
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Delete group controller error', {
      groupId: req.params.groupId,
      error: errorMsg
    });
    res.error('Ошибка удаления группы', 500, {
      groupId: req.params.groupId,
      originalError: errorMsg
    });
  }
});

/**
 * DELETE /api/groups/batch
 * Массовое удаление групп
 */
router.delete('/batch', async (req: Request<{}, ApiResponse, BatchDeleteBody>, res: Response): Promise<void> => {
  try {
    const { groupIds } = req.body;

    if (!groupIds || !Array.isArray(groupIds)) {
      res.error('groupIds должен быть массивом', 400, {
        field: 'groupIds',
        value: groupIds,
        constraint: 'array'
      });
      return;
    }

    if (groupIds.length === 0) {
      res.error('Массив groupIds не может быть пустым', 400, {
        field: 'groupIds',
        constraint: 'non-empty array'
      });
      return;
    }

    // Валидация всех ID
    const validGroupIds: number[] = [];
    for (const id of groupIds) {
      const numId = Number(id);
      if (isNaN(numId) || numId <= 0) {
        res.error(`Некорректный ID группы: ${id}. Все ID должны быть положительными числами`, 400, {
          field: 'groupIds',
          invalidId: id,
          constraint: 'positive numbers'
        });
        return;
      }
      validGroupIds.push(numId);
    }

    const result = await groupsService.deleteGroups(validGroupIds);

    if (result.success) {
      res.status(200).json(result);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Delete groups batch controller error', {
      groupIds: req.body.groupIds,
      error: errorMsg
    });
    res.error('Внутренняя ошибка сервера', 500);
  }
});

/**
 * GET /api/groups/stats
 * GET /api/groups/:taskId/stats
 * Получение статистики по группам
 */
router.get('/stats', async (req: Request, res: Response): Promise<void> => {
  try {
    const result = await groupsService.getGroupsStats();

    if (result.success) {
      res.success(result.data, 'Операция выполнена успешно');
    } else {
      res.error(result.message || 'Ошибка выполнения операции', 500);
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get groups stats controller error', {
      error: errorMsg
    });
    res.error('Внутренняя ошибка сервера', 500);
  }
});

/**
 * GET /api/groups/:taskId/stats
 * Получение статистики по группам для конкретной задачи
 */
router.get('/:taskId/stats', async (req: Request<{ taskId: string }>, res: Response): Promise<void> => {
  try {
    const { taskId } = req.params;

    // Валидация taskId
    if (!taskId || typeof taskId !== 'string') {
      res.status(400).json({
        success: false,
        error: 'INVALID_TASK_ID',
        message: 'Task ID is required'
      });
      return;
    }

    const result = await groupsService.getGroupsStats(taskId);

    if (result.success) {
      res.success(result.data, 'Операция выполнена успешно');
    } else {
      res.error(result.message || 'Ошибка выполнения операции', 500);
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get groups stats controller error', {
      taskId: req.params.taskId,
      error: errorMsg
    });
    res.error('Внутренняя ошибка сервера', 500);
  }
});

export default router;