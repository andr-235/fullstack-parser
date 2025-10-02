/**
 * @fileoverview Интерфейс репозитория VK API (Domain Layer)
 *
 * Определяет контракт для работы с VK API без привязки к библиотекам (vk-io, axios).
 * Реализация находится в Infrastructure Layer.
 *
 * ПРИНЦИП DEPENDENCY INVERSION:
 * - Domain определяет интерфейс для получения данных из VK
 * - Infrastructure реализует через vk-io или другую библиотеку
 */

import { VkId } from '@domain/value-objects/VkId';

/**
 * Информация о группе из VK API
 * Минимальный набор данных, который нужен domain логике
 */
export interface VkGroupInfo {
  readonly id: number;
  readonly name: string;
  readonly screenName: string;
  readonly description: string | null;
  readonly photo50: string | null;
  readonly membersCount: number;
  readonly isClosed: 0 | 1 | 2; // 0 = открытая, 1 = закрытая, 2 = приватная
}

/**
 * Информация о посте из VK API
 */
export interface VkPostInfo {
  readonly id: number;
  readonly ownerId: number;
  readonly fromId: number;
  readonly date: Date;
  readonly text: string;
  readonly commentsCount: number;
  readonly likesCount: number;
  readonly repostsCount: number;
  readonly viewsCount: number;
}

/**
 * Комментарий из VK API
 */
export interface VkCommentInfo {
  readonly id: number;
  readonly postId: number;
  readonly fromId: number;
  readonly date: Date;
  readonly text: string;
  readonly likesCount: number;
  readonly replyToUser: number | null;
  readonly replyToComment: number | null;
}

/**
 * Результат батч-запроса к VK API
 */
export interface VkApiBatchResult<T> {
  readonly successful: readonly T[];
  readonly failed: readonly {
    readonly identifier: string | number;
    readonly error: string;
  }[];
}

/**
 * Интерфейс репозитория для работы с VK API
 *
 * @description
 * Предоставляет методы для получения данных из VKontakte.
 * Скрывает детали работы с VK API от domain логики.
 */
export interface IVkApiRepository {
  /**
   * Получает информацию о группе по ID или screen_name
   *
   * @param identifier - VK ID группы или screen_name
   * @throws VkApiError если группа не найдена или API вернул ошибку
   */
  getGroupInfo(identifier: VkId | string): Promise<VkGroupInfo>;

  /**
   * Получает информацию о нескольких группах одновременно
   * Поддерживает батчинг для оптимизации запросов
   *
   * @param identifiers - массив VK ID или screen_name
   * @returns результат с успешными и неудачными запросами
   */
  getGroupsInfo(identifiers: ReadonlyArray<VkId | string>): Promise<VkApiBatchResult<VkGroupInfo>>;

  /**
   * Проверяет доступность группы (существует и доступна)
   *
   * @param identifier - VK ID группы или screen_name
   * @returns true если группа существует и доступна
   */
  isGroupAccessible(identifier: VkId | string): Promise<boolean>;

  /**
   * Получает информацию о посте
   *
   * @param ownerId - ID владельца поста (отрицательный для групп)
   * @param postId - ID поста
   */
  getPost(ownerId: number, postId: number): Promise<VkPostInfo>;

  /**
   * Получает комментарии к посту
   *
   * @param ownerId - ID владельца поста
   * @param postId - ID поста
   * @param options - опции пагинации и сортировки
   */
  getPostComments(
    ownerId: number,
    postId: number,
    options?: {
      readonly offset?: number;
      readonly count?: number;
      readonly sort?: 'asc' | 'desc';
      readonly needLikes?: boolean;
    }
  ): Promise<readonly VkCommentInfo[]>;

  /**
   * Проверяет валидность access token
   * @returns true если токен валиден
   */
  isTokenValid(): Promise<boolean>;

  /**
   * Получает информацию о текущем пользователе (владельце токена)
   */
  getCurrentUser(): Promise<{
    readonly id: number;
    readonly firstName: string;
    readonly lastName: string;
  }>;
}
