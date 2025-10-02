/**
 * @fileoverview Domain Layer - главный экспорт
 *
 * Центральная точка экспорта всех элементов Domain Layer.
 * Domain Layer содержит бизнес-логику приложения и не зависит от внешних библиотек.
 *
 * CLEAN ARCHITECTURE ПРИНЦИПЫ:
 * - Domain не зависит от Infrastructure
 * - Domain не зависит от Application
 * - Domain определяет интерфейсы (Dependency Inversion)
 * - Domain содержит бизнес-правила
 */

// Entities - экспортируем явно для избежания конфликтов
export {
  Group,
  type CreateGroupProps,
  Task,
  type TaskStatus,
  type TaskProgress,
  type CreateTaskProps,
  GroupUploadTask,
  type GroupUploadProgress,
  type CreateGroupUploadTaskProps,
  VkCollectTask,
  type VkCollectProgress,
  type CreateVkCollectTaskProps
} from './entities';

// Value Objects
export { VkId, GroupId, TaskId, GroupStatus } from './value-objects';

// Repository Interfaces
export type {
  IGroupsRepository,
  FindGroupsOptions,
  FindGroupsResult,
  GroupsStatistics,
  IVkApiRepository,
  VkGroupInfo,
  VkPostInfo,
  VkCommentInfo,
  VkApiBatchResult,
  ITaskStorageRepository,
  TaskInfo,
  GroupUploadTask as GroupUploadTaskInfo,
  VkCollectTask as VkCollectTaskInfo,
  IQueueRepository,
  QueueJobOptions,
  QueueJob,
  QueueStats,
  JobStatus
} from './repositories';

// Domain Errors через Shared
export {
  DomainError,
  ValidationError,
  BusinessRuleError,
  InvariantViolationError
} from '@domain/errors/DomainError';
