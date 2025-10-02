/**
 * @fileoverview Domain Entities
 *
 * Экспорт всех Entity из Domain Layer.
 *
 * ENTITY ПРИНЦИПЫ:
 * - Имеет уникальный идентификатор
 * - Инкапсулирует бизнес-логику
 * - Защищает инварианты
 * - Сравнивается по ID, а не по значению
 * - Управляет своим жизненным циклом
 */

export { Group, CreateGroupProps } from './Group';
export { Task, TaskStatus, TaskProgress, CreateTaskProps } from './Task';
export {
  GroupUploadTask,
  GroupUploadProgress,
  CreateGroupUploadTaskProps
} from './GroupUploadTask';
export {
  VkCollectTask,
  VkCollectProgress,
  CreateVkCollectTaskProps
} from './VkCollectTask';
