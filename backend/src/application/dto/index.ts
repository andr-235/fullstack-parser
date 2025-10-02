/**
 * @fileoverview Application DTOs
 *
 * Экспорт всех Data Transfer Objects.
 */

// Upload Groups DTOs
export type {
  UploadGroupsInput,
  UploadGroupsOutput
} from './UploadGroupsDto';

// Get Groups DTOs
export type {
  GetGroupsInput,
  GetGroupsOutput,
  GroupDto
} from './GetGroupsDto';

// Delete Group DTOs
export type {
  DeleteGroupInput,
  DeleteGroupsInput,
  DeleteGroupOutput
} from './DeleteGroupDto';

// Group Stats DTOs
export type {
  GetGroupStatsInput,
  GroupStatsOutput
} from './GroupStatsDto';
