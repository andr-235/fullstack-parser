/**
 * @fileoverview Application Layer
 *
 * Центральная точка экспорта Use Cases и DTOs.
 * Application Layer содержит бизнес-логику приложения (Use Cases).
 *
 * CLEAN ARCHITECTURE ПРИНЦИПЫ:
 * - Use Cases оркеструют Domain Entities
 * - Use Cases зависят только от Domain интерфейсов
 * - Use Cases не знают о деталях Infrastructure
 * - DTOs определяют границы Use Cases
 */

// Groups Use Cases
export {
  UploadGroupsUseCase,
  GetGroupsUseCase,
  DeleteGroupUseCase,
  GetGroupStatsUseCase
} from './use-cases/groups';

// DTOs
export type {
  UploadGroupsInput,
  UploadGroupsOutput,
  GetGroupsInput,
  GetGroupsOutput,
  GroupDto,
  DeleteGroupInput,
  DeleteGroupsInput,
  DeleteGroupOutput,
  GetGroupStatsInput,
  GroupStatsOutput
} from './dto';
