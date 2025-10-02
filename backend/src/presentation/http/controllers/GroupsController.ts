/**
 * @fileoverview GroupsController - контроллер для управления группами
 *
 * PRESENTATION LAYER
 * - Обрабатывает HTTP запросы
 * - Валидирует входные данные
 * - Вызывает Use Cases через фабрики
 * - Форматирует HTTP ответы
 */

import express, { Request, Response } from 'express';
import { uploadSingle, handleUploadError, validateUploadedFile, logFileUpload } from '@presentation/middleware/upload';
import { GroupsUseCasesFactory } from '@presentation/factories';
import logger from '@infrastructure/utils/logger';
import { ApiResponse } from '@presentation/types/express';
import {
  GroupsUploadResponse,
  GroupsListResponse
} from '@presentation/types/api';
import {
  ValidationError,
  NotFoundError,
  ErrorUtils
} from '@infrastructure/utils/errors';
import {
  validateQuery,
  validateParams,
  validateBody
} from '@presentation/middleware/zodValidation';
import {
  UploadGroupsQuerySchema,
  GetGroupsQuerySchema,
  DeleteGroupParamSchema,
  BatchDeleteGroupsBodySchema,
  type UploadGroupsQuery,
  type GetGroupsQuery,
  type DeleteGroupParam,
  type BatchDeleteGroupsBody
} from '@presentation/validation';

const router = express.Router();

// ============ Route Handlers ============

/**
 * POST /api/groups/upload - Загрузка файла с группами
 */
const uploadGroups = async (req: Request<{}, ApiResponse, {}, UploadGroupsQuery>, res: Response): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;

  try {
    // Валидация файла
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

    // Получаем Use Case из фабрики
    const uploadUseCase = GroupsUseCasesFactory.getUploadGroupsUseCase();

    // Подготавливаем input для Use Case
    const encoding: BufferEncoding = (req.query.encoding as BufferEncoding) || 'utf-8';
    const input = {
      file: req.file.buffer,
      encoding,
      fileName: req.file.originalname
    };

    // Выполняем Use Case
    const result = await uploadUseCase.execute(input);

    logger.info('Groups upload successful', {
      taskId: result.taskId,
      totalGroups: result.totalGroups,
      requestId
    });

    // Форматируем ответ согласно API типу
    const responseData = {
      taskId: result.taskId,
      totalGroups: result.totalGroups,
      validGroups: 0,
      invalidGroups: 0,
      duplicateGroups: 0,
      status: 'processing' as const
    };

    res.success(responseData, result.message || 'Файл с группами успешно загружен');

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
 * GET /api/groups - Получение списка групп с пагинацией и фильтрацией
 */
const getGroups = async (req: Request, res: Response): Promise<void> => {
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

    // Получаем Use Case из фабрики
    const getGroupsUseCase = GroupsUseCasesFactory.getGetGroupsUseCase();

    // Подготавливаем input для Use Case
    const page = Number(validatedQuery.page) || 1;
    const limit = Number(validatedQuery.limit) || 20;
    const offset = (page - 1) * limit;

    const input = {
      limit,
      offset,
      status: validatedQuery.status,
      search: validatedQuery.search,
      sortBy: validatedQuery.sortBy,
      sortOrder: validatedQuery.sortOrder
    };

    // Выполняем Use Case
    const result = await getGroupsUseCase.execute(input);

    // Маппим GroupDto к GroupsListItem
    const groups = result.groups.map(group => ({
      id: group.id,
      vkId: group.vkId,
      name: group.name,
      screenName: group.screenName,
      photo50: group.photo50,
      description: group.description,
      membersCount: group.membersCount,
      isClosed: group.isClosed,
      status: group.status,
      uploadedAt: group.uploadedAt,
      vkUrl: group.vkUrl
    }));

    const pagination = {
      page,
      limit,
      total: result.total,
      totalPages: Math.ceil(result.total / limit),
      hasNext: page < Math.ceil(result.total / limit),
      hasPrev: page > 1
    };

    logger.info('Groups fetched successfully', {
      count: groups.length,
      total: result.total,
      requestId
    });

    // res.success автоматически обернет в ApiResponse формат
    res.json({
      success: true,
      data: groups,
      pagination,
      message: 'Группы успешно получены'
    });

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get groups controller error', {
      error: errorMsg,
      requestId
    });

    const appError = ErrorUtils.toAppError(error as Error, 'Ошибка получения групп');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

/**
 * GET /api/groups/stats - Получение статистики по группам
 */
const getGroupStats = async (req: Request, res: Response): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;

  try {
    logger.info('Processing getGroupStats request', { requestId });

    // Получаем Use Case из фабрики
    const getStatsUseCase = GroupsUseCasesFactory.getGetGroupStatsUseCase();

    // Выполняем Use Case
    const result = await getStatsUseCase.execute({});

    logger.info('Group stats fetched successfully', {
      total: result.total,
      requestId
    });

    res.success(result, 'Статистика получена');

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get group stats controller error', {
      error: errorMsg,
      requestId
    });

    const appError = ErrorUtils.toAppError(error as Error, 'Ошибка получения статистики');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

/**
 * DELETE /api/groups/:id - Удаление группы
 */
const deleteGroup = async (req: Request<DeleteGroupParam>, res: Response): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;
  // Валидация через middleware, используем провалидированное значение
  const groupId = Number(req.params.id);

  try {

    logger.info('Processing deleteGroup request', { groupId, requestId });

    // Получаем Use Case из фабрики
    const deleteUseCase = GroupsUseCasesFactory.getDeleteGroupUseCase();

    // Выполняем Use Case
    await deleteUseCase.execute({ groupId });

    logger.info('Group deleted successfully', { groupId, requestId });

    res.success(null, 'Группа успешно удалена');

  } catch (error) {
    if (error instanceof ValidationError || error instanceof NotFoundError) {
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
 * DELETE /api/groups - Массовое удаление групп
 */
const batchDeleteGroups = async (req: Request<{}, ApiResponse, BatchDeleteGroupsBody>, res: Response): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;
  const { groupIds } = req.body;

  try {
    logger.info('Processing batch delete request', {
      count: groupIds?.length || 0,
      requestId
    });

    // Получаем Use Case из фабрики
    const deleteUseCase = GroupsUseCasesFactory.getDeleteGroupUseCase();

    // Выполняем Use Case для каждой группы
    const deletePromises = groupIds.map(id =>
      deleteUseCase.execute({ groupId: id }).catch(error => ({
        id,
        error: error.message
      }))
    );

    const results = await Promise.all(deletePromises);

    // Подсчитываем успешные и проваленные удаления
    const failed = results.filter(r => r && typeof r === 'object' && 'error' in r);
    const deleted = groupIds.length - failed.length;

    logger.info('Batch delete completed', {
      deleted,
      failed: failed.length,
      requestId
    });

    res.success(
      {
        deleted,
        failed: failed.length,
        errors: failed
      },
      `Удалено ${deleted} из ${groupIds.length} групп`
    );

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Batch delete controller error', {
      error: errorMsg,
      requestId
    });

    const appError = ErrorUtils.toAppError(error as Error, 'Ошибка массового удаления');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

// ============ Routes Configuration ============

router.post(
  '/upload',
  uploadSingle,
  logFileUpload,
  validateUploadedFile,
  validateQuery(UploadGroupsQuerySchema),
  handleUploadError,
  uploadGroups
);

router.get(
  '/',
  validateQuery(GetGroupsQuerySchema),
  getGroups
);

router.get('/stats', getGroupStats);

router.delete(
  '/:id',
  validateParams(DeleteGroupParamSchema),
  deleteGroup
);

router.delete(
  '/',
  validateBody(BatchDeleteGroupsBodySchema),
  batchDeleteGroups
);

export default router;
