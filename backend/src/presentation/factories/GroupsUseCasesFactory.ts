/**
 * @fileoverview GroupsUseCasesFactory - фабрика для создания Groups Use Cases
 *
 * Упрощает получение Use Cases в контроллерах.
 */

import { getContainer } from '@infrastructure/di';
import { UploadGroupsUseCase } from '@application/use-cases/groups/UploadGroupsUseCase';
import { GetGroupsUseCase } from '@application/use-cases/groups/GetGroupsUseCase';
import { DeleteGroupUseCase } from '@application/use-cases/groups/DeleteGroupUseCase';
import { GetGroupStatsUseCase } from '@application/use-cases/groups/GetGroupStatsUseCase';

/**
 * Фабрика для Groups Use Cases
 *
 * @description
 * Предоставляет централизованный доступ к Use Cases для Groups модуля.
 * Использует DI Container для получения настроенных экземпляров.
 */
export class GroupsUseCasesFactory {
  /**
   * Получает UploadGroupsUseCase
   */
  static getUploadGroupsUseCase(): UploadGroupsUseCase {
    const container = getContainer();
    return container.getUploadGroupsUseCase();
  }

  /**
   * Получает GetGroupsUseCase
   */
  static getGetGroupsUseCase(): GetGroupsUseCase {
    const container = getContainer();
    return container.getGetGroupsUseCase();
  }

  /**
   * Получает DeleteGroupUseCase
   */
  static getDeleteGroupUseCase(): DeleteGroupUseCase {
    const container = getContainer();
    return container.getDeleteGroupUseCase();
  }

  /**
   * Получает GetGroupStatsUseCase
   */
  static getGetGroupStatsUseCase(): GetGroupStatsUseCase {
    const container = getContainer();
    return container.getGetGroupStatsUseCase();
  }
}
