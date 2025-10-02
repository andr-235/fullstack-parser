import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import logger from '@infrastructure/utils/logger';

/**
 * Middleware для добавления requestId и инициализации контекста
 * Использует собственную генерацию UUID для избежания конфликтов типов
 */
export const requestContextMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const requestId = uuidv4();
  req.id = requestId;
  req.requestId = requestId;

  // Устанавливаем заголовок
  res.setHeader('X-Request-ID', requestId);

  next();
};

/**
 * Middleware для инициализации контекста запроса
 */
export const initRequestContext = (req: Request, res: Response, next: NextFunction) => {
  req.startTime = Date.now();

  req.context = {
    requestId: req.requestId, // используем собственный requestId
    startTime: req.startTime,
    userAgent: req.get('User-Agent'),
    ip: req.ip || req.socket.remoteAddress,
    path: req.path,
    method: req.method
  };

  // Логируем входящий запрос
  logger.info('Incoming request', {
    requestId: req.requestId,
    method: req.method,
    path: req.path,
    userAgent: req.context.userAgent,
    ip: req.context.ip
  });

  next();
};

export default {
  requestContextMiddleware,
  initRequestContext
};