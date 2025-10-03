/**
 * @fileoverview DI Container - контейнер зависимостей
 *
 * Реализует паттерн Dependency Injection для управления зависимостями приложения.
 */

import { PrismaClient } from '@prisma/client';
import Redis from 'ioredis';

// Domain Repositories
import { IGroupsRepository } from '@domain/repositories/IGroupsRepository';
import { IVkApiRepository } from '@domain/repositories/IVkApiRepository';
import { ITaskStorageRepository } from '@domain/repositories/ITaskStorageRepository';
import { IFileParser } from '@domain/repositories/IFileParser';
import { IQueueRepository } from '@domain/repositories/IQueueRepository';

// Infrastructure Adapters
import { PrismaGroupsRepository } from '@infrastructure/database/repositories/PrismaGroupsRepository';
import { VkApiAdapter } from '@infrastructure/external-services/vk-api/VkApiAdapter';
import { RedisTaskStorageAdapter } from '@infrastructure/storage/RedisTaskStorageAdapter';
import { FileParserAdapter } from '@infrastructure/external-services/file-parser/FileParserAdapter';
import { BullMQAdapter } from '@infrastructure/queue/BullMQAdapter';
import { WorkerManager } from '@infrastructure/queue/workers/WorkerManager';

// Use Cases
import { UploadGroupsUseCase } from '@application/use-cases/groups/UploadGroupsUseCase';
import { GetGroupsUseCase } from '@application/use-cases/groups/GetGroupsUseCase';
import { DeleteGroupUseCase } from '@application/use-cases/groups/DeleteGroupUseCase';
import { GetGroupStatsUseCase } from '@application/use-cases/groups/GetGroupStatsUseCase';

import logger from '@infrastructure/utils/logger';

/**
 * Dependency Injection Container
 *
 * @description
 * Централизованное управление зависимостями приложения.
 * Следует принципу Dependency Inversion из Clean Architecture.
 */
export class Container {
  // Infrastructure dependencies
  private _prisma: PrismaClient | null = null;
  private _redis: Redis | null = null;

  // Repositories
  private _groupsRepository: IGroupsRepository | null = null;
  private _vkApiRepository: IVkApiRepository | null = null;
  private _taskStorageRepository: ITaskStorageRepository | null = null;
  private _fileParser: IFileParser | null = null;
  private _queueRepository: IQueueRepository | null = null;

  // Queue Infrastructure
  private _workerManager: WorkerManager | null = null;

  // Use Cases
  private _uploadGroupsUseCase: UploadGroupsUseCase | null = null;
  private _getGroupsUseCase: GetGroupsUseCase | null = null;
  private _deleteGroupUseCase: DeleteGroupUseCase | null = null;
  private _getGroupStatsUseCase: GetGroupStatsUseCase | null = null;

  constructor(
    private readonly vkAccessToken: string
  ) {
    logger.info('DI Container initializing');
  }

  // ============ Infrastructure ============

  /**
   * Получает Prisma Client
   */
  getPrisma(): PrismaClient {
    if (!this._prisma) {
      this._prisma = new PrismaClient({
        log: process.env.NODE_ENV === 'development'
          ? ['query', 'error', 'warn']
          : ['error']
      });
      logger.info('Prisma Client created');
    }
    return this._prisma;
  }

  /**
   * Получает Redis Client
   */
  getRedis(): Redis {
    if (!this._redis) {
      this._redis = new Redis({
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379', 10),
        password: process.env.REDIS_PASSWORD,
        maxRetriesPerRequest: null, // Required for BullMQ
        retryStrategy: (times) => {
          const delay = Math.min(times * 50, 2000);
          return delay;
        }
      });

      this._redis.on('connect', () => {
        logger.info('Redis connected');
      });

      this._redis.on('error', (error) => {
        logger.error('Redis error', { error: error.message });
      });

      logger.info('Redis Client created');
    }
    return this._redis;
  }

  // ============ Repositories ============

  /**
   * Получает Groups Repository
   */
  getGroupsRepository(): IGroupsRepository {
    if (!this._groupsRepository) {
      this._groupsRepository = new PrismaGroupsRepository();
      logger.info('GroupsRepository created');
    }
    return this._groupsRepository;
  }

  /**
   * Получает VK API Repository
   */
  getVkApiRepository(): IVkApiRepository {
    if (!this._vkApiRepository) {
      this._vkApiRepository = new VkApiAdapter(this.vkAccessToken);
      logger.info('VkApiRepository created');
    }
    return this._vkApiRepository;
  }

  /**
   * Получает Task Storage Repository
   */
  getTaskStorageRepository(): ITaskStorageRepository {
    if (!this._taskStorageRepository) {
      const redis = this.getRedis();
      this._taskStorageRepository = new RedisTaskStorageAdapter(redis);
      logger.info('TaskStorageRepository created');
    }
    return this._taskStorageRepository;
  }

  /**
   * Получает File Parser
   */
  getFileParser(): IFileParser {
    if (!this._fileParser) {
      this._fileParser = new FileParserAdapter();
      logger.info('FileParser created');
    }
    return this._fileParser;
  }

  /**
   * Получает Queue Repository
   */
  getQueueRepository(): IQueueRepository {
    if (!this._queueRepository) {
      const redis = this.getRedis();
      this._queueRepository = new BullMQAdapter(redis);
      logger.info('QueueRepository created');
    }
    return this._queueRepository;
  }

  // ============ Queue Infrastructure ============

  /**
   * Получает Worker Manager
   */
  getWorkerManager(): WorkerManager {
    if (!this._workerManager) {
      this._workerManager = new WorkerManager(this);
      logger.info('WorkerManager created');
    }
    return this._workerManager;
  }

  // ============ Use Cases ============

  /**
   * Получает UploadGroupsUseCase
   */
  getUploadGroupsUseCase(): UploadGroupsUseCase {
    if (!this._uploadGroupsUseCase) {
      this._uploadGroupsUseCase = new UploadGroupsUseCase(
        this.getGroupsRepository(),
        this.getVkApiRepository(),
        this.getTaskStorageRepository(),
        this.getFileParser(),
        this.getQueueRepository() // Добавлена зависимость от очереди
      );
      logger.info('UploadGroupsUseCase created');
    }
    return this._uploadGroupsUseCase;
  }

  /**
   * Получает GetGroupsUseCase
   */
  getGetGroupsUseCase(): GetGroupsUseCase {
    if (!this._getGroupsUseCase) {
      this._getGroupsUseCase = new GetGroupsUseCase(
        this.getGroupsRepository()
      );
      logger.info('GetGroupsUseCase created');
    }
    return this._getGroupsUseCase;
  }

  /**
   * Получает DeleteGroupUseCase
   */
  getDeleteGroupUseCase(): DeleteGroupUseCase {
    if (!this._deleteGroupUseCase) {
      this._deleteGroupUseCase = new DeleteGroupUseCase(
        this.getGroupsRepository()
      );
      logger.info('DeleteGroupUseCase created');
    }
    return this._deleteGroupUseCase;
  }

  /**
   * Получает GetGroupStatsUseCase
   */
  getGetGroupStatsUseCase(): GetGroupStatsUseCase {
    if (!this._getGroupStatsUseCase) {
      this._getGroupStatsUseCase = new GetGroupStatsUseCase(
        this.getGroupsRepository()
      );
      logger.info('GetGroupStatsUseCase created');
    }
    return this._getGroupStatsUseCase;
  }

  // ============ Lifecycle ============

  /**
   * Закрывает все соединения
   */
  async dispose(): Promise<void> {
    logger.info('DI Container disposing');

    const promises: Promise<void>[] = [];

    // Останавливаем worker'ы
    if (this._workerManager) {
      promises.push(
        this._workerManager.stopAll()
          .then(() => logger.info('WorkerManager stopped'))
          .catch(error => logger.error('WorkerManager stop error', { error: error.message }))
      );
    }

    // Закрываем очереди
    if (this._queueRepository && this._queueRepository instanceof BullMQAdapter) {
      promises.push(
        this._queueRepository.closeAll()
          .then(() => logger.info('Queues closed'))
          .catch(error => logger.error('Queues close error', { error: error.message }))
      );
    }

    if (this._prisma) {
      promises.push(
        this._prisma.$disconnect()
          .then(() => logger.info('Prisma disconnected'))
          .catch(error => logger.error('Prisma disconnect error', { error: error.message }))
      );
    }

    if (this._redis) {
      promises.push(
        this._redis.quit()
          .then(() => logger.info('Redis disconnected'))
          .catch(error => logger.error('Redis disconnect error', { error: error.message }))
      );
    }

    await Promise.all(promises);
    logger.info('DI Container disposed');
  }
}
