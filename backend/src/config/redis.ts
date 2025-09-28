import IORedis from 'ioredis';
import logger from '@/utils/logger';
import { QueueRedisConfig } from '@/types/queue';

/**
 * Получает конфигурацию Redis из переменных окружения
 */
function getRedisConfig(): QueueRedisConfig {
  return {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD,
    db: parseInt(process.env.REDIS_DB || '0', 10),
    maxRetriesPerRequest: null, // Required for BullMQ
    connectTimeout: 30000, // Увеличен до 30 секунд
    commandTimeout: 300000, // Увеличен до 5 минут для VK API
    retryDelayOnFailover: 100,
    enableOfflineQueue: false,
    lazyConnect: true,
    keepAlive: 30000, // Keep-alive каждые 30 секунд
  };
}

/**
 * Создает новое соединение с Redis
 */
export function createRedisConnection(config?: Partial<QueueRedisConfig>): IORedis {
  const redisConfig = { ...getRedisConfig(), ...config };

  const redis = new IORedis({
    host: redisConfig.host,
    port: redisConfig.port,
    password: redisConfig.password,
    db: redisConfig.db,
    maxRetriesPerRequest: redisConfig.maxRetriesPerRequest,
    connectTimeout: redisConfig.connectTimeout,
    commandTimeout: redisConfig.commandTimeout,
    enableOfflineQueue: redisConfig.enableOfflineQueue,
    lazyConnect: redisConfig.lazyConnect,
    keepAlive: redisConfig.keepAlive,
    enableReadyCheck: true,
    // Настройки retry для стабильности
    retryStrategy: (times) => {
      const delay = Math.min(times * 50, 2000);
      return delay;
    }
  });

  // Обработчики событий для логирования
  redis.on('connect', () => {
    logger.info('Redis connection established', {
      host: redisConfig.host,
      port: redisConfig.port,
      db: redisConfig.db
    });
  });

  redis.on('ready', () => {
    logger.info('Redis connection ready');
  });

  redis.on('error', (error) => {
    logger.error('Redis connection error', {
      error: error.message,
      stack: error.stack
    });
  });

  redis.on('close', () => {
    logger.info('Redis connection closed');
  });

  redis.on('reconnecting', (ms) => {
    logger.warn('Redis reconnecting', { delay: ms });
  });

  return redis;
}

/**
 * Проверяет соединение с Redis
 */
export async function testRedisConnection(redis?: IORedis): Promise<boolean> {
  const connection = redis || createRedisConnection();

  try {
    await connection.ping();
    logger.info('Redis ping successful');
    return true;
  } catch (error) {
    logger.error('Redis ping failed', { error: (error as Error).message });
    return false;
  } finally {
    if (!redis) {
      // Закрываем тестовое соединение
      connection.disconnect();
    }
  }
}

/**
 * Получает информацию о Redis сервере
 */
export async function getRedisInfo(redis: IORedis): Promise<{
  version: string;
  usedMemory: string;
  connectedClients: number;
  uptime: number;
}> {
  try {
    const info = await redis.info();
    const lines = info.split('\r\n');

    const getInfoValue = (key: string): string => {
      const line = lines.find(l => l.startsWith(`${key}:`));
      return line ? line.split(':')[1] : 'unknown';
    };

    return {
      version: getInfoValue('redis_version'),
      usedMemory: getInfoValue('used_memory_human'),
      connectedClients: parseInt(getInfoValue('connected_clients'), 10) || 0,
      uptime: parseInt(getInfoValue('uptime_in_seconds'), 10) || 0,
    };
  } catch (error) {
    logger.error('Failed to get Redis info', { error: (error as Error).message });
    throw error;
  }
}

/**
 * Очищает Redis базу данных (только для разработки!)
 */
export async function flushRedisDb(redis: IORedis): Promise<void> {
  if (process.env.NODE_ENV === 'production') {
    throw new Error('Database flush is not allowed in production');
  }

  try {
    await redis.flushdb();
    logger.warn('Redis database flushed', {
      environment: process.env.NODE_ENV,
      db: await redis.config('GET', 'database')
    });
  } catch (error) {
    logger.error('Failed to flush Redis database', { error: (error as Error).message });
    throw error;
  }
}

// Экспорт конфигурации для использования в других модулях
export const redisConfig = getRedisConfig();