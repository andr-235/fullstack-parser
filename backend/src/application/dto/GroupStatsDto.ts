/**
 * @fileoverview DTOs для статистики групп
 */

/**
 * Input DTO для получения статистики
 */
export interface GetGroupStatsInput {
  readonly taskId?: string;
}

/**
 * Output DTO для статистики групп
 */
export interface GroupStatsOutput {
  readonly total: number;
  readonly valid: number;
  readonly invalid: number;
  readonly duplicate: number;
  readonly validPercent: number;
  readonly invalidPercent: number;
  readonly duplicatePercent: number;
}
