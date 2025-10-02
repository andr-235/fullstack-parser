/**
 * @fileoverview GetGroupStatsUseCase - Use Case получения статистики по группам
 */

import { IGroupsRepository } from '@domain/repositories/IGroupsRepository';
import { GetGroupStatsInput, GroupStatsOutput } from '@application/dto/GroupStatsDto';

/**
 * Use Case: Получение статистики по группам
 *
 * @description
 * Получает агрегированную статистику:
 * - Общее количество групп
 * - Валидные/невалидные/дубликаты
 * - Процентное соотношение
 *
 * @example
 * ```typescript
 * const useCase = new GetGroupStatsUseCase(groupsRepo);
 *
 * // Статистика по всем группам
 * const stats = await useCase.execute({});
 *
 * // Статистика по конкретной задаче
 * const taskStats = await useCase.execute({ taskId: 'task-123' });
 * ```
 */
export class GetGroupStatsUseCase {
  constructor(
    private readonly groupsRepository: IGroupsRepository
  ) {}

  /**
   * Выполняет Use Case
   */
  async execute(input: GetGroupStatsInput): Promise<GroupStatsOutput> {
    // Шаг 1: Получаем статистику из репозитория
    const stats = await this.groupsRepository.getStatistics(input.taskId);

    // Шаг 2: Вычисляем проценты
    const validPercent = this.calculatePercent(stats.valid, stats.total);
    const invalidPercent = this.calculatePercent(stats.invalid, stats.total);
    const duplicatePercent = this.calculatePercent(stats.duplicate, stats.total);

    // Шаг 3: Возвращаем обогащенную статистику
    return {
      total: stats.total,
      valid: stats.valid,
      invalid: stats.invalid,
      duplicate: stats.duplicate,
      validPercent,
      invalidPercent,
      duplicatePercent
    };
  }

  /**
   * Вычисляет процент
   */
  private calculatePercent(value: number, total: number): number {
    if (total === 0) {
      return 0;
    }

    return Math.round((value / total) * 100);
  }
}
