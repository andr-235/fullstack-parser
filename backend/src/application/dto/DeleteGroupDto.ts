/**
 * @fileoverview DTOs для удаления групп
 */

/**
 * Input DTO для удаления группы
 */
export interface DeleteGroupInput {
  readonly groupId: number;
}

/**
 * Input DTO для массового удаления групп
 */
export interface DeleteGroupsInput {
  readonly groupIds: readonly number[];
}

/**
 * Output DTO для удаления
 */
export interface DeleteGroupOutput {
  readonly deletedCount: number;
  readonly message: string;
}
