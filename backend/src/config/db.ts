import { PrismaService, prisma } from './prisma';
import { DatabaseConfig, Environment } from '@/types/database';
import logger from '@/utils/logger';

const environment = (process.env.NODE_ENV as Environment) || 'development';
const dbUrl = process.env.DB_URL;

if (!dbUrl) {
  throw new Error('DB_URL environment variable is required');
}

// Legacy config для обратной совместимости с существующим API
const legacyConfig = {
  pool: {
    max: 20,
    min: 0,
    acquire: 60000,
    idle: 10000,
    evict: 1000
  },
  define: {
    timestamps: true,
    underscored: false,
    freezeTableName: false
  },
  logging: environment === 'development',
  benchmark: environment === 'development'
};

/**
 * Проверяет подключение к базе данных
 */
export async function testConnection(): Promise<boolean> {
  try {
    await PrismaService.connect();
    logger.info('Database connection established successfully', {
      database: 'vk_analyzer',
      provider: 'postgresql'
    });
    return true;
  } catch (error) {
    logger.error('Unable to connect to database', error);
    return false;
  }
}

/**
 * Закрывает все соединения с базой данных
 */
export async function closeConnection(): Promise<void> {
  try {
    await PrismaService.disconnect();
    logger.info('Database connections closed');
  } catch (error) {
    logger.error('Error closing database connections', error);
    throw error;
  }
}

/**
 * Синхронизирует модели с базой данных (заглушка для Prisma)
 */
export async function syncModels(force = false): Promise<void> {
  try {
    // Prisma управляет схемой через миграции
    await prisma.$queryRaw`SELECT 1`;
    logger.info('Database schema verified', { force, note: 'Prisma manages schema via migrations' });
  } catch (error) {
    logger.error('Error verifying database schema', error);
    throw error;
  }
}

/**
 * Выполняет миграции базы данных
 */
export async function runMigrations(): Promise<void> {
  try {
    await PrismaService.runMigrations();
    logger.info('Database migrations completed');
  } catch (error) {
    logger.error('Error running database migrations', error);
    throw error;
  }
}

/**
 * Получает конфигурацию базы данных
 */
export function getDatabaseConfig(): DatabaseConfig {
  const url = new URL(dbUrl!);
  return {
    username: url.username || 'postgres',
    password: url.password || '',
    database: url.pathname.slice(1) || 'vk_analyzer',
    host: url.hostname || 'localhost',
    port: Number(url.port) || 5432,
    dialect: 'postgresql' as const,
    logging: legacyConfig.logging,
    pool: legacyConfig.pool,
    define: legacyConfig.define
  };
}

/**
 * Проверяет здоровье базы данных
 */
export async function healthCheck(): Promise<{
  status: 'healthy' | 'unhealthy';
  latency?: number;
  error?: string;
  connectionStats?: any;
}> {
  return await PrismaService.healthCheck();
}

// Экспорт Prisma клиента вместо Sequelize
export default prisma;
export { prisma };

// Экспорт дополнительных утилит
export { PrismaService };
export const db = prisma;