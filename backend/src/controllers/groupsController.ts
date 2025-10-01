import express, { Request, Response } from 'express';
import Joi from 'joi';
import { uploadSingle, handleUploadError, validateUploadedFile, logFileUpload } from '@/middleware/upload';
import groupsService from '@/services/groupsService';
import logger from '@/utils/logger';
import { ApiResponse, PaginationParams } from '@/types/express';
import { GetGroupsParams } from '@/services/groupsService';
import {
  GroupsUploadResponse,
  GroupsListResponse
} from '@/types/api';
import {
  ValidationError,
  NotFoundError,
  ErrorUtils
} from '@/utils/errors';
import { validateBody, validateQuery, validateGroupIdParam, paginationSchema } from '@/middleware/validationMiddleware';

const router = express.Router();

// Validation schemas
const uploadQuerySchema = Joi.object({
  encoding: Joi.string().valid('utf-8', 'utf8', 'ascii', 'base64', 'hex').default('utf-8')
});

const getGroupsQuerySchema = Joi.object({
  page: Joi.number().integer().min(1).default(1),
  limit: Joi.number().integer().min(1).max(10000).default(20),
  status: Joi.string().valid('all', 'active', 'inactive', 'pending').optional(),
  search: Joi.string().allow('').min(0).max(255).optional(),
  sortBy: Joi.string().valid('id', 'name', 'vkId', 'createdAt', 'updatedAt', 'uploadedAt', 'uploaded_at').default('id'),
  sortOrder: Joi.string().valid('ASC', 'DESC', 'asc', 'desc').default('ASC')
}).options({ convert: true, allowUnknown: true, stripUnknown: false });

const batchDeleteSchema = Joi.object({
  groupIds: Joi.array().items(Joi.number().integer().positive()).min(1).max(100).required()
});

// Типы для запросов
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
 * POST /api/groups/upload - Загрузка файла с группами
 */
const uploadGroups = async (req: Request<{}, ApiResponse, {}, UploadQuery>, res: Response): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;

  try {
    if (!req.file) {
      const validationError = new ValidationError('Файл не был загружен', [
        {
          field: 'file',
          message: 'File is required',
          value: undefined
        }
      ]);
      if (requestId) {
        validationError.setRequestId(requestId);
      }
      throw validationError;
    }

    logger.info('Groups upload started', {
      filename: req.file.originalname,
      size: req.file.size,
      mimetype: req.file.mimetype,
      requestId
    });

    const encoding: BufferEncoding = (req.query.encoding as BufferEncoding) || 'utf-8';
    logger.info('Processing file with groupsService', { encoding, requestId });

    const result = await groupsService.uploadGroups(req.file.buffer, encoding);

    if (result.success) {
      logger.info('Groups upload successful', {
        taskId: result.data?.taskId,
        totalGroups: result.data?.totalGroups || 0,
        requestId
      });
      res.success(result.data, 'Файл с группами успешно загружен');
    } else {
      logger.warn('Groups upload failed', {
        error: result.error,
        message: result.message,
        requestId
      });
      res.error(result.message || 'Ошибка обработки файла', 400, {
        details: result.error
      });
    }

  } catch (error) {
    if (error instanceof ValidationError) {
      throw error;
    }

    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Upload groups controller error', {
      filename: req.file?.originalname,
      error: errorMsg,
      requestId
    });

    const appError = ErrorUtils.toAppError(error as Error, 'Ошибка загрузки файла');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

/**
 * GET /api/groups/upload/:taskId/status - Получение статуса загрузки
 */
const getUploadStatus = async (req: Request<{ taskId: string }>, res: Response): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;
  const { taskId } = req.params;

  try {
    const result = await groupsService.getUploadStatus(taskId);

    if (result.success) {
      res.success(result.data, 'Статус загрузки получен');
    } else {
      const notFoundError = new NotFoundError('Upload task', taskId);
      if (requestId) {
        notFoundError.setRequestId(requestId);
      }
      throw notFoundError;
    }

  } catch (error) {
    if (error instanceof NotFoundError) {
      throw error;
    }

    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get upload status controller error', {
      taskId,
      error: errorMsg,
      requestId
    });

    const appError = ErrorUtils.toAppError(error as Error, 'Ошибка получения статуса загрузки');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

/**
 * GET /api/groups - Получение списка групп с пагинацией и фильтрацией
 */
const getGroups = async (req: Request<{}, ApiResponse, {}, GetGroupsQuery>, res: Response): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;
  const validatedQuery = (req as any).validatedQuery || req.query;

  try {
    logger.info('Processing getGroups request', {
      page: validatedQuery.page,
      limit: validatedQuery.limit,
      status: validatedQuery.status,
      search: validatedQuery.search,
      sortBy: validatedQuery.sortBy,
      sortOrder: validatedQuery.sortOrder,
      requestId
    });

    const page = Number(validatedQuery.page) || 1;
    const limit = Number(validatedQuery.limit) || 20;
    const offset = (page - 1) * limit;

    // Маппинг параметров для repo
    let mappedStatus = validatedQuery.status;
    if (mappedStatus === 'all') {
      mappedStatus = undefined;
    } else if (mappedStatus) {
      // Маппинг frontend статусов к БД enum
      const statusMap: { [key: string]: string } = {
        active: 'valid',
        inactive: 'invalid',
        pending: 'duplicate'
      };
      mappedStatus = statusMap[mappedStatus as keyof typeof statusMap] || mappedStatus;
    }

    let mappedSearch = validatedQuery.search;
    if (mappedSearch === '') {
      mappedSearch = undefined;
    }

    let mappedSortBy = validatedQuery.sortBy || 'id';
    if (mappedSortBy === 'uploadedAt') {
      mappedSortBy = 'uploaded_at';
    }

    const params: GetGroupsParams = {
      limit: limit,
      offset: offset,
      status: mappedStatus,
      search: mappedSearch,
      sortBy: mappedSortBy,
      sortOrder: validatedQuery.sortOrder || 'ASC'
    };

    const result = await groupsService.getGroups(params);

    if (result.success) {
      logger.info('Groups retrieved successfully', {
        totalGroups: result.data?.total || 0,
        page,
        limit,
        requestId
      });

      const totalPages = Math.ceil((result.data?.total || 0) / limit);

      res.paginated(result.data?.groups || [], {
        page,
        limit,
        total: result.data?.total || 0,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1
      }, {
        filters: {
          status: params.status,
          search: params.search
        },
        sorting: {
          sortBy: params.sortBy,
          sortOrder: params.sortOrder
        }
      });
    } else {
      res.error(result.message || 'Ошибка получения списка групп', 500);
    }

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get groups controller error', {
      error: errorMsg,
      requestId
    });

    const appError = ErrorUtils.toAppError(error as Error, 'Ошибка получения списка групп');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

/**
 * DELETE /api/groups/:groupId - Удаление группы по ID
 */
const deleteGroup = async (req: Request<{ groupId: string }>, res: Response): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;
  const groupId = (req as any).validatedGroupId; // Получаем из middleware

  try {
    logger.info('Processing deleteGroup request', { groupId, requestId });

    const result = await groupsService.deleteGroup(groupId);

    if (result.success) {
      logger.info('Group deleted successfully', { groupId, requestId });
      res.success({
        deletedGroupId: groupId,
        deletedAt: new Date().toISOString()
      }, 'Группа успешно удалена');
    } else {
      const notFoundError = new NotFoundError('Group', String(groupId));
      if (requestId) {
        notFoundError.setRequestId(requestId);
      }
      throw notFoundError;
    }

  } catch (error) {
    if (error instanceof NotFoundError) {
      throw error;
    }

    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Delete group controller error', {
      groupId,
      error: errorMsg,
      requestId
    });

    const appError = ErrorUtils.toAppError(error as Error, 'Ошибка удаления группы');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

/**
 * DELETE /api/groups/batch - Массовое удаление групп
 */
const deleteGroups = async (req: Request<{}, ApiResponse, BatchDeleteBody>, res: Response): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;

  try {
    logger.info('Processing batch deleteGroups request', {
      groupsCount: req.body.groupIds?.length,
      requestId
    });

    const { groupIds } = req.body;
    const result = await groupsService.deleteGroups(groupIds);

    if (result.success) {
      logger.info('Groups batch deleted successfully', {
        deletedCount: result.data?.deletedCount || 0,
        requestedCount: groupIds.length,
        requestId
      });

      res.success({
        deletedGroupIds: groupIds,
        deletedCount: result.data?.deletedCount || 0,
        requestedCount: groupIds.length,
        deletedAt: new Date().toISOString()
      }, `Успешно удалено групп: ${result.data?.deletedCount || 0} из ${groupIds.length}`);
    } else {
      res.error(result.message || 'Ошибка массового удаления групп', 500, {
        failedGroupIds: groupIds
      });
    }

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Batch delete groups controller error', {
      groupsCount: req.body.groupIds?.length,
      error: errorMsg,
      requestId
    });

    const appError = ErrorUtils.toAppError(error as Error, 'Ошибка массового удаления групп');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

/**
 * DELETE /api/groups/all - Удаление всех групп из БД
 */
const deleteAllGroups = async (req: Request, res: Response): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;

  try {
    logger.warn('Processing deleteAllGroups request - deleting ALL groups from database', { requestId });

    const result = await groupsService.deleteAllGroups();

    if (result.success) {
      logger.info('All groups deleted successfully', {
        deletedCount: result.data?.deletedCount || 0,
        requestId
      });

      res.success({
        deletedCount: result.data?.deletedCount || 0,
        deletedAt: new Date().toISOString()
      }, `Успешно удалено групп: ${result.data?.deletedCount || 0}`);
    } else {
      res.error(result.message || 'Ошибка удаления всех групп', 500);
    }

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Delete all groups controller error', {
      error: errorMsg,
      requestId
    });

    const appError = ErrorUtils.toAppError(error as Error, 'Ошибка удаления всех групп');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

// Маршруты
router.post(
  '/groups/upload',
  logFileUpload,
  uploadSingle,
  handleUploadError,
  validateUploadedFile,
  validateQuery(uploadQuerySchema),
  uploadGroups
);

router.get('/groups/upload/:taskId/status', getUploadStatus);
router.get('/groups', validateQuery(getGroupsQuerySchema), getGroups);
router.delete('/groups/all', deleteAllGroups);
router.delete('/groups/:groupId', validateGroupIdParam, deleteGroup);
router.delete('/groups/batch', validateBody(batchDeleteSchema), deleteGroups);

export default router;