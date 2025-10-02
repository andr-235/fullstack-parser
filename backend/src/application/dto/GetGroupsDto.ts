/**
 * @fileoverview DTOs для получения групп
 */

/**
 * Input DTO для получения списка групп
 */
export interface GetGroupsInput {
  readonly limit?: number;
  readonly offset?: number;
  readonly status?: 'all' | 'valid' | 'invalid' | 'duplicate';
  readonly search?: string;
  readonly sortBy?: 'uploaded_at' | 'name' | 'members_count' | 'status';
  readonly sortOrder?: 'asc' | 'desc';
}

/**
 * Output DTO для одной группы
 */
export interface GroupDto {
  readonly id: number;
  readonly vkId: number;
  readonly name: string;
  readonly screenName: string | null;
  readonly photo50: string | null;
  readonly membersCount: number | null;
  readonly isClosed: number;
  readonly description: string | null;
  readonly status: string;
  readonly uploadedAt: string;
  readonly vkUrl: string;
}

/**
 * Output DTO для списка групп с пагинацией
 */
export interface GetGroupsOutput {
  readonly groups: readonly GroupDto[];
  readonly total: number;
  readonly pagination: {
    readonly limit: number;
    readonly offset: number;
    readonly hasMore: boolean;
  };
}
