import { Request, Response, NextFunction } from 'express';
import helmet from 'helmet';

/**
 * Основной security middleware с использованием helmet
 */
export const securityHeaders = helmet({
  // Базовые настройки безопасности
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'"],
      fontSrc: ["'self'"],
      objectSrc: ["'none'"],
      mediaSrc: ["'self'"],
      frameSrc: ["'none'"]
    }
  },
  crossOriginEmbedderPolicy: false, // Отключаем для API
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
});

/**
 * Кастомные заголовки для API
 */
export const apiHeaders = (req: Request, res: Response, next: NextFunction) => {
  // API версия
  res.setHeader('X-API-Version', process.env.API_VERSION || '1.0.0');

  // Брендинг
  res.setHeader('X-Powered-By', 'VK Analytics API');

  // Кеширование
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');

  next();
};

export default {
  securityHeaders,
  apiHeaders
};