/**
 * @fileoverview DTOs для загрузки групп
 *
 * Data Transfer Objects для границ Use Case.
 * Определяют контракт входных и выходных данных.
 */

/**
 * Input DTO для загрузки групп
 */
export interface UploadGroupsInput {
  readonly file: Buffer;
  readonly encoding: BufferEncoding;
  readonly fileName?: string;
}

/**
 * Output DTO для загрузки групп
 */
export interface UploadGroupsOutput {
  readonly taskId: string;
  readonly totalGroups: number;
  readonly message: string;
}
