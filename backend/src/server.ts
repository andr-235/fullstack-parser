import crypto from 'crypto';
import express, { Request, Response, NextFunction, Application } from 'express';
import cors from 'cors';

import logger from '@/utils/logger';
import sequelize, { testConnection, healthCheck } from '@/config/db';
import taskController from '@/controllers/taskController';
import groupsController from '@/controllers/groupsController';
import { ApiResponse } from '@/types/express';

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

// Middleware для логирования входящих запросов
app.use((req: RequestWithId, res: Response, next: NextFunction): void => {
  const requestId = crypto.randomUUID();
  req.id = requestId;

  // Санитизация body: маскировка токенов
  const sanitizedBody: any = { ...req.body };
  if (sanitizedBody.token) {
    sanitizedBody.token = '***';
  }
  if (sanitizedBody.access_token) {
    sanitizedBody.access_token = '***';
  }

  // Санитизация headers: удаление Authorization если есть
  const sanitizedHeaders: any = { ...req.headers };
  if (sanitizedHeaders.authorization) {
    sanitizedHeaders.authorization = '***';
  }
  if (sanitizedHeaders['x-api-key']) {
    sanitizedHeaders['x-api-key'] = '***';
  }

  logger.info('Incoming request', {
    method: req.method,
    url: req.url,
    query: req.query,
    body: Object.keys(sanitizedBody).length > 0 ? sanitizedBody : undefined,
    userAgent: req.get('User-Agent'),
    ip: req.ip,
    id: requestId
  });

  // Логируем завершение запроса
  const startTime = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    logger.info('Request completed', {
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      duration: `${duration}ms`,
      id: requestId
    });
  });

  next();
});

// Middleware для обработки ошибок JSON
app.use((err: Error, req: Request, res: Response, next: NextFunction): void => {
  if (err instanceof SyntaxError && 'body' in err) {
    const response: ApiResponse = {
      success: false,
      error: 'INVALID_JSON',
      message: 'Invalid JSON in request body'
    };

    logger.warn('Invalid JSON in request', {
      url: req.url,
      method: req.method,
      error: err.message,
      id: (req as RequestWithId).id
    });

    res.status(400).json(response);
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
  allowedHeaders: ['Content-Type', 'Authorization', 'X-API-Key']
}));

// Request timeout middleware
app.use((req: Request, res: Response, next: NextFunction): void => {
  const timeout = 30000; // 30 seconds
  const timer = setTimeout(() => {
    if (!res.headersSent) {
      const response: ApiResponse = {
        success: false,
        error: 'REQUEST_TIMEOUT',
        message: 'Request timeout'
      };
      res.status(408).json(response);
    }
  }, timeout);

  res.on('finish', () => clearTimeout(timer));
  next();
});

// Rate limiting would go here if needed
// app.use(rateLimitMiddleware);

// Basic route
app.get('/', (req: Request, res: Response): void => {
  const response: ApiResponse = {
    success: true,
    message: 'Express VK Backend is running!',
    data: {
      version: '1.0.0',
      timestamp: new Date().toISOString(),
      environment: process.env.NODE_ENV || 'development'
    }
  };
  res.json(response);
});

// Health check endpoint for deployment monitoring
app.get('/api/health', async (req: Request, res: Response): Promise<void> => {
  try {
    // Check database connection
    const dbHealth = await healthCheck();

    const healthResponse: HealthCheckResponse = {
      status: dbHealth.status === 'healthy' ? 'healthy' : 'unhealthy',
      timestamp: new Date().toISOString(),
      services: {
        database: dbHealth.status === 'healthy' ? 'connected' : 'disconnected',
        server: 'running'
      },
      uptime: process.uptime()
    };

    const statusCode = dbHealth.status === 'healthy' ? 200 : 503;
    res.status(statusCode).json(healthResponse);
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Health check failed', { error: errorMsg });

    const errorResponse: HealthCheckResponse = {
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: errorMsg
    };

    res.status(503).json(errorResponse);
  }
});

// Detailed health check endpoint
app.get('/api/health/detailed', async (req: Request, res: Response): Promise<void> => {
  try {
    const dbHealth = await healthCheck();

    const response = {
      status: dbHealth.status === 'healthy' ? 'healthy' : 'unhealthy',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '1.0.0',
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      services: {
        database: {
          status: dbHealth.status === 'healthy' ? 'connected' : 'disconnected',
          latency: dbHealth.latency,
          error: dbHealth.error
        },
        server: {
          status: 'running',
          port: PORT,
          memory: process.memoryUsage(),
          pid: process.pid
        }
      }
    };

    const statusCode = dbHealth.status === 'healthy' ? 200 : 503;
    res.status(statusCode).json(response);
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Detailed health check failed', { error: errorMsg });
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: errorMsg
    });
  }
});

// API routes
app.use('/api', taskController);
app.use('/api/groups', groupsController);

// Глобальный middleware для 404 ошибок
app.use((req: Request, res: Response, next: NextFunction): void => {
  logger.warn('404 Not Found', {
    method: req.method,
    url: req.url,
    query: req.query,
    id: (req as RequestWithId).id
  });

  const response: ApiResponse = {
    success: false,
    error: 'NOT_FOUND',
    message: `Route ${req.method} ${req.url} not found`
  };

  res.status(404).json(response);
});

// Глобальный обработчик ошибок
app.use((error: Error, req: Request, res: Response, next: NextFunction): void => {
  logger.error('Unhandled server error', {
    error: error.message,
    stack: error.stack,
    method: req.method,
    url: req.url,
    id: (req as RequestWithId).id
  });

  if (res.headersSent) {
    return next(error);
  }

  const response: ApiResponse = {
    success: false,
    error: 'INTERNAL_SERVER_ERROR',
    message: process.env.NODE_ENV === 'production'
      ? 'Internal server error'
      : error.message
  };

  res.status(500).json(response);
});

// Graceful shutdown handler
const gracefulShutdown = async (signal: string): Promise<void> => {
  logger.info(`Received ${signal}, starting graceful shutdown`);

  try {
    // Close database connections
    await sequelize.close();
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
process.on('unhandledRejection', (reason: any, promise: Promise<any>) => {
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

    // Test database connection
    const connected = await testConnection();
    if (!connected) {
      throw new Error('Failed to connect to database');
    }

    // Sync database models
    await sequelize.sync({ force: false });
    logger.info('Database models synchronized');

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

    // Export app for testing
    module.exports = app;

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Failed to start server', { error: errorMsg });
    process.exit(1);
  }
}

// Start the server
if (require.main === module) {
  startServer();
}

export default app;