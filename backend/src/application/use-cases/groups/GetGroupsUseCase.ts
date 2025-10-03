/**
 * @fileoverview GetGroupsUseCase - Use Case получения списка групп
 */

import { IGroupsRepository, FindGroupsOptions } from '@domain/repositories/IGroupsRepository';
import { Group } from '@domain/entities/Group';
import { GetGroupsInput, GetGroupsOutput, GroupDto } from '@application/dto/GetGroupsDto';
import { GroupStatus as PrismaGroupStatus } from '@prisma/client';

/**
 * Use Case: Получение списка групп с фильтрацией
 *
 * @description
 * Получает группы из репозитория с применением фильтров и пагинации.
 * Преобразует Domain Entities в DTOs для API.
 *
 * @example
 * ```typescript
 * const useCase = new GetGroupsUseCase(groupsRepo);
 *
 * const result = await useCase.execute({
 *   limit: 20,
 *   offset: 0,
 *   status: 'valid',
 *   search: 'tech'
 * });
 * ```
 */
export class GetGroupsUseCase {
  constructor(
    private readonly groupsRepository: IGroupsRepository
  ) {}

  /**
   * Выполняет Use Case
   */
  async execute(input: GetGroupsInput): Promise<GetGroupsOutput> {
    // Шаг 1: Подготовка параметров для репозитория
    const options = this.mapInputToOptions(input);

    // Шаг 2: Получаем группы из репозитория
    const result = await this.groupsRepository.findAll(options);

    // Шаг 3: Преобразуем Domain Entities в DTOs
    const groupDtos = result.groups.map(group => this.mapGroupToDto(group));

    // Шаг 4: Возвращаем результат
    return {
      groups: groupDtos,
      total: result.total,
      pagination: {
        limit: options.limit || 20,
        offset: options.offset || 0,
        hasMore: result.hasMore
      }
    };
  }

  /**
   * Преобразует Input DTO в опции репозитория
   */
  private mapInputToOptions(input: GetGroupsInput): FindGroupsOptions {
    // Маппинг статусов: frontend -> database
    let status: PrismaGroupStatus | 'all' = 'all';
    if (input.status && input.status !== 'all') {
      const statusMap: Record<string, PrismaGroupStatus> = {
        'valid': 'valid',
        'invalid': 'invalid',
        'duplicate': 'duplicate'
      };
      status = statusMap[input.status] || 'all';
    }

    // Нормализация sortBy: преобразуем camelCase в snake_case для БД
    const sortBy = this.normalizeSortBy(input.sortBy);

    return {
      limit: input.limit || 20,
      offset: input.offset || 0,
      status,
      search: input.search,
      sortBy,
      sortOrder: input.sortOrder || 'desc'
    };
  }

  /**
   * Нормализует поле сортировки
   * Преобразует различные варианты написания в формат БД (snake_case)
   */
  private normalizeSortBy(sortBy?: string): string {
    if (!sortBy) {
      return 'uploaded_at';
    }

    // Маппинг всех вариантов на формат БД
    const sortByMap: Record<string, string> = {
      'id': 'id',
      'uploadedAt': 'uploaded_at',
      'uploaded_at': 'uploaded_at',
      'name': 'name',
      'vkId': 'vk_id',
      'vk_id': 'vk_id',
      'membersCount': 'members_count',
      'members_count': 'members_count',
      'status': 'status',
      'createdAt': 'created_at',
      'created_at': 'created_at',
      'updatedAt': 'updated_at',
      'updated_at': 'updated_at'
    };

    return sortByMap[sortBy] || 'uploaded_at';
  }

  /**
   * Преобразует Group Entity в DTO
   */
  private mapGroupToDto(group: Group): GroupDto {
    return {
      id: group.id?.value || 0,
      vkId: group.vkId.value,
      name: group.name,
      screenName: group.screenName,
      photo50: group.photo50,
      membersCount: group.membersCount,
      isClosed: group.isClosed,
      description: group.description,
      status: group.status.value,
      uploadedAt: group.uploadedAt.toISOString(),
      vkUrl: group.getVkUrl()
    };
  }
}
