/**
 * @fileoverview DeleteGroupUseCase - Use Case удаления групп
 */

import { IGroupsRepository } from '@domain/repositories/IGroupsRepository';
import { GroupId } from '@domain/value-objects/GroupId';
import { DeleteGroupInput, DeleteGroupsInput, DeleteGroupOutput } from '@application/dto/DeleteGroupDto';
import { DomainError } from '@domain/errors/DomainError';

/**
 * Use Case: Удаление группы или групп
 *
 * @description
 * Удаляет одну или несколько групп из системы.
 * Проверяет существование перед удалением.
 *
 * @example
 * ```typescript
 * const useCase = new DeleteGroupUseCase(groupsRepo);
 *
 * // Удаление одной группы
 * const result = await useCase.execute({ groupId: 123 });
 *
 * // Массовое удаление
 * const result = await useCase.executeMany({ groupIds: [1, 2, 3] });
 * ```
 */
export class DeleteGroupUseCase {
  constructor(
    private readonly groupsRepository: IGroupsRepository
  ) {}

  /**
   * Удаляет одну группу
   */
  async execute(input: DeleteGroupInput): Promise<DeleteGroupOutput> {
    // Шаг 1: Создаем GroupId Value Object
    const groupId = GroupId.create(input.groupId);

    // Шаг 2: Проверяем существование группы
    const group = await this.groupsRepository.findById(groupId);
    if (!group) {
      throw new DomainError(
        `Group with ID ${input.groupId} not found`,
        'GROUP_NOT_FOUND',
        { groupId: input.groupId }
      );
    }

    // Шаг 3: Удаляем группу
    const deleted = await this.groupsRepository.delete(groupId);

    if (!deleted) {
      throw new DomainError(
        `Failed to delete group ${input.groupId}`,
        'DELETE_FAILED',
        { groupId: input.groupId }
      );
    }

    // Шаг 4: Возвращаем результат
    return {
      deletedCount: 1,
      message: `Группа ${group.name} успешно удалена`
    };
  }

  /**
   * Массовое удаление групп
   */
  async executeMany(input: DeleteGroupsInput): Promise<DeleteGroupOutput> {
    // Шаг 1: Валидация входных данных
    if (!input.groupIds || input.groupIds.length === 0) {
      throw new DomainError(
        'No group IDs provided for deletion',
        'INVALID_INPUT'
      );
    }

    if (input.groupIds.length > 100) {
      throw new DomainError(
        'Cannot delete more than 100 groups at once',
        'TOO_MANY_GROUPS',
        { count: input.groupIds.length }
      );
    }

    // Шаг 2: Создаем GroupId Value Objects
    const groupIds = input.groupIds.map(id => GroupId.create(id));

    // Шаг 3: Удаляем группы
    const deletedCount = await this.groupsRepository.deleteMany(groupIds);

    // Шаг 4: Возвращаем результат
    return {
      deletedCount,
      message: `Успешно удалено групп: ${deletedCount} из ${input.groupIds.length}`
    };
  }

  /**
   * Удаляет все группы (ОПАСНАЯ ОПЕРАЦИЯ!)
   */
  async executeDeleteAll(): Promise<DeleteGroupOutput> {
    // Получаем количество групп перед удалением
    const totalBefore = await this.groupsRepository.count();

    // Удаляем все группы
    const deletedCount = await this.groupsRepository.deleteAll();

    return {
      deletedCount,
      message: `Удалено всего групп: ${deletedCount}`
    };
  }
}
