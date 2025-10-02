/**
 * @fileoverview Domain Repository Interfaces
 *
 * Экспорт всех интерфейсов репозиториев из Domain Layer.
 * Эти интерфейсы определяют контракты для работы с данными,
 * но не содержат реализации (Dependency Inversion Principle).
 */

export type {
  IGroupsRepository,
  FindGroupsOptions,
  FindGroupsResult,
  GroupsStatistics
} from './IGroupsRepository';

export type {
  IVkApiRepository,
  VkGroupInfo,
  VkPostInfo,
  VkCommentInfo,
  VkApiBatchResult
} from './IVkApiRepository';

export type {
  ITaskStorageRepository,
  TaskInfo,
  GroupUploadProgress,
  VkCollectProgress,
  GroupUploadTask,
  VkCollectTask
} from './ITaskStorageRepository';

export type {
  IQueueRepository,
  QueueJobOptions,
  QueueJob,
  QueueStats,
  JobStatus
} from './IQueueRepository';
