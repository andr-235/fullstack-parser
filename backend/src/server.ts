import dotenv from 'dotenv';

// Загружаем переменные окружения в самом начале
dotenv.config();

import crypto from 'crypto';
import express, { Request, Response, NextFunction, Application } from 'express';
import cors from 'cors';

import logger from '@/utils/logger';
import { PrismaService } from '@/config/prisma';
import { queueService } from '@/services/queueService';
import { setupRoutes } from '@/routes';
import { ApiResponse } from '@/types/express';
import {
  requestIdMiddleware,
  responseHeaders,
  responseLogger
} from '@/middleware/responseFormatter';

const app: Application = express();
const PORT = process.env.PORT ? parseInt(process.env.PORT) : 3000;

// Интерфейсы для типизации middleware
interface RequestWithId extends Request {
  id: string;
}

interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  services?: {
    database: string;
    server: string;
  };
  uptime?: number;
  error?: string;
}

// === СТАНДАРТИЗИРОВАННЫЕ MIDDLEWARE ===

// Request ID и контекст запроса
app.use(requestIdMiddleware);

// Стандартные заголовки ответа
app.use(responseHeaders);

// Логирование ответов (опционально, для отладки)
if (process.env.NODE_ENV === 'development') {
  app.use(responseLogger);
}

// Middleware для обработки ошибок JSON
app.use((err: Error, req: Request, res: Response, next: NextFunction): void => {
  if (err instanceof SyntaxError && 'body' in err) {
    logger.warn('Invalid JSON in request', {
      url: req.url,
      method: req.method,
      error: err.message,
      id: (req as RequestWithId).id
    });

    res.error('Invalid JSON in request body', 400);
    return;
  }
  next(err);
});

// Basic middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// CORS configuration
const corsOrigins = (process.env.CORS_ORIGINS || 'http://localhost:5173')
  .split(',')
  .map(origin => origin.trim());

app.use(cors({
  origin: corsOrigins,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: [
    'Content-Type',
    'Authorization',
    'X-API-Key',
    'expires',
    'cache-control',
    'pragma',
    'if-modified-since',
    'x-requested-with'
  ]
}));

// Request timeout middleware
app.use((req: Request, res: Response, next: NextFunction): void => {
  const timeout = 30000; // 30 seconds
  const timer = setTimeout(() => {
    if (!res.headersSent) {
      res.error('Request timeout', 408);
    }
  }, timeout);

  res.on('finish', () => clearTimeout(timer));
  next();
});

// Rate limiting would go here if needed
// app.use(rateLimitMiddleware);

// Basic route с использованием стандартизированного ответа
app.get('/', (req: Request, res: Response): void => {
  res.json({
    success: true,
    data: {
      version: '1.0.0',
      environment: process.env.NODE_ENV || 'development',
      uptime: process.uptime()
    },
    message: 'Express VK Backend is running!',
    timestamp: new Date().toISOString()
  });
});

// === НАСТРОЙКА МАРШРУТОВ ===
// Используем централизованную систему маршрутизации
// Она включает в себя responseFormatter и errorHandler
setupRoutes(app);

// Graceful shutdown handler
const gracefulShutdown = async (signal: string): Promise<void> => {
  logger.info(`Received ${signal}, starting graceful shutdown`);

  try {
    // Close queue service and workers
    await queueService.cleanup();
    logger.info('Queue service and workers stopped');

    // Close database connections
    await PrismaService.disconnect();
    logger.info('Database connections closed');

    // Exit process
    process.exit(0);
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Error during graceful shutdown', { error: errorMsg });
    process.exit(1);
  }
};

// Register shutdown handlers
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason: any) => {
  logger.error('Unhandled Rejection', {
    reason: reason?.toString(),
    stack: reason?.stack
  });
});

// Handle uncaught exceptions
process.on('uncaughtException', (error: Error) => {
  logger.error('Uncaught Exception', {
    error: error.message,
    stack: error.stack
  });
  process.exit(1);
});

// Initialize database and start server
async function startServer(): Promise<void> {
  try {
    logger.info('Starting server initialization...');

    // Connect to database via Prisma
    await PrismaService.connect();
    logger.info('Prisma connected to database');

    // Database connection already tested via PrismaService.connect()

    // Initialize queue service and workers
    logger.info('Initializing BullMQ queue service and workers...');
    await queueService.initialize();
    logger.info('BullMQ queue service and workers initialized successfully');

    // Start HTTP server
    const server = app.listen(PORT, () => {
      logger.info(`Server running on port ${PORT}`, {
        environment: process.env.NODE_ENV || 'development',
        port: PORT,
        corsOrigins,
        pid: process.pid
      });
    });

    // Handle server errors
    server.on('error', (error: Error) => {
      logger.error('Server error', { error: error.message });
    });

    // Verify queue service health after startup
    const queueHealth = await queueService.healthCheck();
    logger.info('Queue service health check after startup', queueHealth);

    // Export app for testing
    module.exports = app;

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Failed to start server', { error: errorMsg });

    // Attempt cleanup on startup failure
    try {
      await queueService.cleanup();
    } catch (cleanupError) {
      logger.error('Failed to cleanup after startup failure', {
        error: cleanupError instanceof Error ? cleanupError.message : String(cleanupError)
      });
    }

    process.exit(1);
  }
}

// Start the server
if (require.main === module) {
  startServer();
}

export default app;