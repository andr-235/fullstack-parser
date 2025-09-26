import express, { Request, Response } from 'express';
import { uploadSingle, handleUploadError, validateUploadedFile, logFileUpload } from '@/middleware/upload';
import groupsService from '@/services/groupsService';
import logger from '@/utils/logger';
import { ApiResponse, PaginationParams } from '@/types/express';
import { GetGroupsParams } from '@/services/groupsService';

const router = express.Router();

interface UploadQuery {
  encoding?: BufferEncoding;
}

interface GetGroupsQuery extends PaginationParams {
  status?: string;
  search?: string;
  sortBy?: string;
  sortOrder?: 'ASC' | 'DESC';
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
  upload,
  handleUploadError,
  validateUploadedFile,
  async (req: Request<{}, ApiResponse, {}, UploadQuery>, res: Response): Promise<void> => {
    try {
      if (!req.file) {
        res.status(400).json({
          success: false,
          error: 'NO_FILE',
          message: 'No file uploaded'
        });
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
        res.status(200).json(result);
      } else {
        logger.info('Groups upload failed', { error: result.error, message: result.message });
        res.status(400).json(result);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Upload groups controller error', {
        filename: req.file?.originalname,
        error: errorMsg
      });
      res.status(500).json({
        success: false,
        error: 'INTERNAL_ERROR',
        message: 'Internal server error'
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
      res.status(200).json(result);
    } else {
      res.status(404).json(result);
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get upload status controller error', {
      taskId: req.params.taskId,
      error: errorMsg
    });
    res.status(500).json({
      success: false,
      error: 'INTERNAL_ERROR',
      message: 'Internal server error'
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
      sortOrder = 'DESC'
    } = req.query;

    // Валидация параметров
    const pageNum = Number(page);
    const limitNum = Number(limit);

    if (isNaN(pageNum) || pageNum < 1) {
      res.status(400).json({
        success: false,
        error: 'INVALID_PAGE',
        message: 'Page must be a positive number'
      });
      return;
    }

    if (isNaN(limitNum) || limitNum < 1 || limitNum > 100) {
      res.status(400).json({
        success: false,
        error: 'INVALID_LIMIT',
        message: 'Limit must be between 1 and 100'
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
      res.status(200).json({
        success: true,
        data: result.data
      });
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get groups controller error', {
      query: req.query,
      error: errorMsg
    });
    res.status(500).json({
      success: false,
      error: 'INTERNAL_ERROR',
      message: 'Internal server error'
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
      res.status(400).json({
        success: false,
        error: 'INVALID_GROUP_ID',
        message: 'Group ID must be a positive number'
      });
      return;
    }

    const result = await groupsService.deleteGroup(groupId);

    if (result.success) {
      res.status(200).json(result);
    } else {
      const statusCode = result.error === 'GROUP_NOT_FOUND' ? 404 : 400;
      res.status(statusCode).json(result);
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Delete group controller error', {
      groupId: req.params.groupId,
      error: errorMsg
    });
    res.status(500).json({
      success: false,
      error: 'INTERNAL_ERROR',
      message: 'Internal server error'
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
      res.status(400).json({
        success: false,
        error: 'INVALID_GROUP_IDS',
        message: 'groupIds must be an array'
      });
      return;
    }

    if (groupIds.length === 0) {
      res.status(400).json({
        success: false,
        error: 'EMPTY_GROUP_IDS',
        message: 'groupIds array cannot be empty'
      });
      return;
    }

    // Валидация всех ID
    const validGroupIds: number[] = [];
    for (const id of groupIds) {
      const numId = Number(id);
      if (isNaN(numId) || numId <= 0) {
        res.status(400).json({
          success: false,
          error: 'INVALID_GROUP_ID',
          message: `Invalid group ID: ${id}. All IDs must be positive numbers`
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
    res.status(500).json({
      success: false,
      error: 'INTERNAL_ERROR',
      message: 'Internal server error'
    });
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
      res.status(200).json({
        success: true,
        data: result.data
      });
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get groups stats controller error', {
      error: errorMsg
    });
    res.status(500).json({
      success: false,
      error: 'INTERNAL_ERROR',
      message: 'Internal server error'
    });
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
      res.status(200).json({
        success: true,
        data: result.data
      });
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get groups stats controller error', {
      taskId: req.params.taskId,
      error: errorMsg
    });
    res.status(500).json({
      success: false,
      error: 'INTERNAL_ERROR',
      message: 'Internal server error'
    });
  }
});

export default router;