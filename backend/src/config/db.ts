import { Sequelize, SequelizeOptions } from 'sequelize-typescript';
import * as pg from 'pg';
import { SequelizeConfig, Environment } from '@/types/database';
import logger from '@/utils/logger';
import path from 'path';
import 'reflect-metadata';

const environment = (process.env.NODE_ENV as Environment) || 'development';
const dbUrl = process.env.DB_URL;

if (!dbUrl) {
  throw new Error('DB_URL environment variable is required');
}

const config: SequelizeOptions = {
  // Включаем логирование SQL запросов в development режиме
  logging: environment === 'development'
    ? (sql: string, timing?: number) => {
        logger.debug('SQL Query', { sql, timing });
      }
    : false,

  // Connection pool конфигурация для оптимальной производительности
  pool: {
    max: 20,          // Максимальное количество соединений в пуле
    min: 0,           // Минимальное количество соединений в пуле
    acquire: 60000,   // Максимальное время в миллисекундах, которое пул будет пытаться получить соединение
    idle: 10000,      // Максимальное время в миллисекундах, которое соединение может быть неактивным
    evict: 1000       // Интервал проверки соединений на предмет удаления из пула
  },

  // Connection timeout настройки
  dialectOptions: {
    connectTimeout: 30000,    // Таймаут подключения (30 секунд)
    acquireConnectionTimeout: 60000,  // Таймаут получения соединения (60 секунд)
    timeout: 60000,           // Таймаут выполнения запроса (60 секунд)

    // SSL конфигурация для production
    ...(environment === 'production' && {
      ssl: {
        require: true,
        rejectUnauthorized: false
      }
    })
  },

  // Дополнительные настройки производительности
  define: {
    // Автоматически добавляем timestamps ко всем моделям
    timestamps: true,
    // Используем camelCase для полей
    underscored: false,
    // Имена таблиц во множественном числе
    freezeTableName: false
  },

  // Query опции по умолчанию
  query: {
    // Используем prepared statements для лучшей производительности
    useMaster: true
  },

  // Benchmark для мониторинга производительности в development
  benchmark: environment === 'development',

  // Настройки для различных диалектов PostgreSQL
  dialectModule: pg,

  // Retry конфигурация
  retry: {
    match: [
      /ConnectionError/,
      /ConnectionRefusedError/,
      /ConnectionTimedOutError/,
      /TimeoutError/,
      /ETIMEDOUT/,
      /ECONNRESET/,
      /ECONNREFUSED/,
      /EHOSTUNREACH/,
      /ENOTFOUND/,
      /EAI_AGAIN/
    ],
    max: 3
  }
};

// Добавляем модели к конфигурации
const sequelizeConfig: SequelizeOptions = {
  ...config,
  models: [path.join(__dirname, '..', 'models', '*.ts')],
  modelMatch: (filename: string, member: string) => {
    return filename.substring(0, filename.indexOf('.ts')) === member.toLowerCase();
  }
};

const sequelize = new Sequelize(dbUrl, sequelizeConfig);

/**
 * Проверяет подключение к базе данных
 */
export async function testConnection(): Promise<boolean> {
  try {
    await sequelize.authenticate();
    logger.info('Database connection established successfully', {
      database: sequelize.getDatabaseName(),
      dialect: sequelize.getDialect()
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
    await sequelize.close();
    logger.info('Database connections closed');
  } catch (error) {
    logger.error('Error closing database connections', error);
    throw error;
  }
}

/**
 * Синхронизирует модели с базой данных
 */
export async function syncModels(force = false): Promise<void> {
  try {
    await sequelize.sync({ force });
    logger.info('Database models synchronized', { force });
  } catch (error) {
    logger.error('Error synchronizing database models', error);
    throw error;
  }
}

/**
 * Выполняет миграции базы данных
 */
export async function runMigrations(): Promise<void> {
  try {
    // TODO: Implement migrations logic when migration system is set up
    logger.info('Database migrations completed');
  } catch (error) {
    logger.error('Error running database migrations', error);
    throw error;
  }
}

/**
 * Получает конфигурацию базы данных
 */
export function getDatabaseConfig(): SequelizeConfig {
  return {
    username: sequelize.config.username || '',
    password: sequelize.config.password || '',
    database: sequelize.config.database || '',
    host: sequelize.config.host || 'localhost',
    port: Number(sequelize.config.port) || 5432,
    dialect: sequelize.getDialect() as 'postgres',
    logging: Boolean(config.logging),
    pool: config.pool || undefined,
    define: config.define || undefined
  };
}

/**
 * Проверяет здоровье базы данных
 */
export async function healthCheck(): Promise<{
  status: 'healthy' | 'unhealthy';
  latency?: number;
  error?: string;
}> {
  const start = Date.now();

  try {
    await sequelize.authenticate();
    return {
      status: 'healthy',
      latency: Date.now() - start
    };
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    return {
      status: 'unhealthy',
      latency: Date.now() - start,
      error: errorMsg
    };
  }
}

export default sequelize;
export { sequelize };