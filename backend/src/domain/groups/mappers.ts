/**
 * @fileoverview Data transformation mappers для Groups domain
 *
 * Централизованная логика конвертации между слоями:
 * - VK API (snake_case) → Database (snake_case)
 * - Database (snake_case) → API DTO (camelCase)
 * - Parsed Input → VK Identifiers
 *
 * ПРАВИЛО: Вся трансформация данных ТОЛЬКО через мапперы!
 * НЕ дублировать логику трансформации в других файлах.
 *
 * @example
 * ```typescript
 * import { GroupMapper } from '@/domain/groups/mappers';
 *
 * // VK API → DB
 * const dbInput = GroupMapper.vkToDb(vkGroup, taskId);
 *
 * // DB → API DTO
 * const apiDto = GroupMapper.dbToApi(dbGroup);
 * ```
 */

import {
  VkGroupRaw,
  DbGroup,
  GroupApiDto,
  CreateGroupInput,
  ParsedGroupInput,
  isValidVkId,
  isValidScreenName,
} from './types';
import { GroupStatus } from '@prisma/client';

/**
 * Mappers для трансформации между слоями приложения
 */
export class GroupMapper {
  // ============ VK API → Database ============

  /**
   * Конвертирует VK API данные в формат для создания в БД
   *
   * @param vkData - Данные от VK API (groups.getById)
   * @param taskId - UUID задачи загрузки
   * @returns Данные готовые для Prisma createGroups()
   *
   * @example
   * ```typescript
   * const vkGroup: VkGroupRaw = {
   *   id: 12345,
   *   name: 'Test Group',
   *   screen_name: 'test_group',
   *   description: 'Description',
   *   photo_50: 'https://...',
   *   members_count: 1000,
   *   is_closed: 0
   * };
   *
   * const dbInput = GroupMapper.vkToDb(vkGroup, 'task-uuid');
   * // → CreateGroupInput для БД
   * ```
   */
  static vkToDb(vkData: VkGroupRaw, taskId: string): CreateGroupInput {
    return {
      vk_id: vkData.id,
      name: vkData.name || `Group ${vkData.id}`,
      screen_name: vkData.screen_name || null,
      photo_50: vkData.photo_50 || null,
      members_count: vkData.members_count || 0,
      is_closed: vkData.is_closed ?? 0,
      description: vkData.description || null,
      status: 'valid' as GroupStatus,
      task_id: taskId,
    };
  }

  /**
   * Batch конвертация VK → DB
   * Оптимизировано для массовой обработки
   *
   * @param vkGroups - Массив VK групп
   * @param taskId - UUID задачи
   * @returns Массив готовых для БД данных
   */
  static vkToDbBatch(
    vkGroups: readonly VkGroupRaw[],
    taskId: string
  ): CreateGroupInput[] {
    return vkGroups.map((vk) => this.vkToDb(vk, taskId));
  }

  // ============ Database → API DTO ============

  /**
   * Конвертирует DB запись в API DTO для фронтенда
   *
   * Трансформации:
   * - snake_case → camelCase
   * - null → null (сохраняем для Optional chaining)
   * - Date objects (уже есть из Prisma)
   *
   * @param dbGroup - Запись из БД (Prisma groups model)
   * @returns API DTO с camelCase полями
   *
   * @example
   * ```typescript
   * const dbGroup = await prisma.groups.findUnique({ where: { id: 1 } });
   * const apiDto = GroupMapper.dbToApi(dbGroup);
   * // → GroupApiDto для отправки на frontend
   * ```
   */
  static dbToApi(dbGroup: DbGroup): GroupApiDto {
    return {
      id: dbGroup.id,
      vkId: dbGroup.vk_id,
      name: dbGroup.name || '',
      screenName: dbGroup.screen_name,
      photo50: dbGroup.photo_50,
      membersCount: dbGroup.members_count,
      isClosed: dbGroup.is_closed,
      description: dbGroup.description,
      status: dbGroup.status,
      uploadedAt: dbGroup.uploaded_at,
      taskId: dbGroup.task_id,
    };
  }

  /**
   * Batch конвертация DB → API
   * Оптимизировано для списков
   *
   * @param dbGroups - Массив записей из БД
   * @returns Массив API DTO
   */
  static dbToApiBatch(dbGroups: readonly DbGroup[]): GroupApiDto[] {
    return dbGroups.map((db) => this.dbToApi(db));
  }

  // ============ Parsed Input → VK Identifiers ============

  /**
   * Извлекает VK identifiers из распарсенных данных файла
   *
   * Приоритет извлечения:
   * 1. ID (если валидный number)
   * 2. screenName (если валидный screen_name)
   * 3. name (если похож на screen_name, без пробелов)
   *
   * @param parsed - Результаты парсинга файла
   * @returns Массив VK ID (number) или screen_name (string)
   *
   * @example
   * ```typescript
   * const parsed: ParsedGroupInput[] = [
   *   { id: 12345, name: 'Group Name' },
   *   { name: 'test_group', screenName: 'test_group' },
   *   { name: 'invalid group name' }  // будет пропущен
   * ];
   *
   * const identifiers = GroupMapper.parsedToIdentifiers(parsed);
   * // → [12345, 'test_group']
   * ```
   */
  static parsedToIdentifiers(
    parsed: readonly ParsedGroupInput[]
  ): Array<number | string> {
    return parsed
      .map((p) => {
        // Приоритет 1: Числовой ID
        if (p.id !== undefined && p.id !== null) {
          return isValidVkId(p.id) ? p.id : null;
        }

        // Приоритет 2: Явный screenName
        if (p.screenName) {
          return isValidScreenName(p.screenName) ? p.screenName : null;
        }

        // Приоритет 3: name как потенциальный screen_name
        if (p.name) {
          // Проверяем, может ли name быть screen_name
          // (без пробелов, достаточная длина)
          const cleaned = p.name.trim();
          if (
            !cleaned.includes(' ') &&
            cleaned.length >= 5 &&
            cleaned.length <= 32
          ) {
            return isValidScreenName(cleaned) ? cleaned : null;
          }
        }

        return null;
      })
      .filter((id): id is number | string =>
        id !== null && id !== undefined
      );
  }

  // ============ Validation & Normalization Helpers ============

  /**
   * Нормализует VK group ID (убирает минус если есть)
   *
   * VK API возвращает отрицательные ID для групп в некоторых методах,
   * но groups.getById требует положительные
   *
   * @param id - VK group ID (может быть отрицательным)
   * @returns Положительный VK group ID
   */
  static normalizeVkId(id: number): number {
    return Math.abs(id);
  }

  /**
   * Конвертирует VK group ID в owner_id для wall.get
   *
   * @param groupId - Положительный VK group ID
   * @returns Отрицательный owner_id
   */
  static groupIdToOwnerId(groupId: number): number {
    return -Math.abs(groupId);
  }

  /**
   * Извлекает screen_name из VK URL
   *
   * @param url - VK URL (https://vk.com/screen_name или vk.com/screen_name)
   * @returns screen_name или null если не удалось извлечь
   *
   * @example
   * ```typescript
   * GroupMapper.extractScreenNameFromUrl('https://vk.com/test_group');
   * // → 'test_group'
   *
   * GroupMapper.extractScreenNameFromUrl('vk.com/public12345');
   * // → 'public12345'
   * ```
   */
  static extractScreenNameFromUrl(url: string): string | null {
    try {
      // Очищаем URL
      const cleaned = url.trim().toLowerCase();

      // Убираем протокол
      const withoutProtocol = cleaned.replace(/^https?:\/\//, '');

      // Убираем vk.com/ или m.vk.com/
      const withoutDomain = withoutProtocol.replace(/^(m\.)?vk\.com\//, '');

      // Убираем query params и hash
      const withoutParams = withoutDomain.split(/[?#]/)[0];

      // Убираем trailing slash
      const screenName = withoutParams.replace(/\/$/, '');

      // Валидация
      if (isValidScreenName(screenName)) {
        return screenName;
      }

      return null;
    } catch {
      return null;
    }
  }

  /**
   * Извлекает group ID из VK URL вида /club12345
   *
   * @param url - VK URL
   * @returns Group ID или null
   *
   * @example
   * ```typescript
   * GroupMapper.extractGroupIdFromUrl('https://vk.com/club12345');
   * // → 12345
   *
   * GroupMapper.extractGroupIdFromUrl('vk.com/public67890');
   * // → 67890
   * ```
   */
  static extractGroupIdFromUrl(url: string): number | null {
    try {
      const cleaned = url.trim().toLowerCase();

      // Паттерны: club12345, public12345, event12345
      const match = cleaned.match(/\/(club|public|event)(\d+)/);

      if (match && match[2]) {
        const id = parseInt(match[2], 10);
        return isValidVkId(id) ? id : null;
      }

      return null;
    } catch {
      return null;
    }
  }

  /**
   * Умный парсинг VK identifier из строки
   *
   * Пытается извлечь ID или screen_name из различных форматов:
   * - Чистый ID: "12345"
   * - VK URL: "https://vk.com/test_group"
   * - Club URL: "vk.com/club12345"
   * - Screen name: "test_group"
   *
   * @param input - Строка для парсинга
   * @returns VK ID (number) или screen_name (string) или null
   */
  static parseVkIdentifier(input: string): number | string | null {
    const cleaned = input.trim();

    // Попытка 1: Чистый числовой ID
    if (/^\d+$/.test(cleaned)) {
      const id = parseInt(cleaned, 10);
      return isValidVkId(id) ? id : null;
    }

    // Попытка 2: URL с club/public/event ID
    const groupId = this.extractGroupIdFromUrl(cleaned);
    if (groupId !== null) {
      return groupId;
    }

    // Попытка 3: URL со screen_name
    if (cleaned.includes('vk.com') || cleaned.includes('/')) {
      const screenName = this.extractScreenNameFromUrl(cleaned);
      if (screenName !== null) {
        return screenName;
      }
    }

    // Попытка 4: Чистый screen_name
    if (isValidScreenName(cleaned)) {
      return cleaned;
    }

    return null;
  }

  // ============ Statistics & Aggregation ============

  /**
   * Группирует API DTO по статусу
   *
   * @param groups - Массив GroupApiDto
   * @returns Map со статусами и группами
   */
  static groupByStatus(
    groups: readonly GroupApiDto[]
  ): Map<GroupStatus, GroupApiDto[]> {
    const grouped = new Map<GroupStatus, GroupApiDto[]>();

    for (const group of groups) {
      const existing = grouped.get(group.status) || [];
      existing.push(group);
      grouped.set(group.status, existing);
    }

    return grouped;
  }

  /**
   * Вычисляет статистику по группам
   *
   * @param groups - Массив GroupApiDto
   * @returns Статистика
   */
  static calculateStats(groups: readonly GroupApiDto[]): {
    total: number;
    byStatus: Record<GroupStatus, number>;
    totalMembers: number;
    averageMembers: number;
    closedCount: number;
    openCount: number;
  } {
    const stats = {
      total: groups.length,
      byStatus: {} as Record<GroupStatus, number>,
      totalMembers: 0,
      averageMembers: 0,
      closedCount: 0,
      openCount: 0,
    };

    for (const group of groups) {
      // Статистика по статусам
      stats.byStatus[group.status] = (stats.byStatus[group.status] || 0) + 1;

      // Статистика по участникам
      const members = group.membersCount || 0;
      stats.totalMembers += members;

      // Статистика по типу группы
      if (group.isClosed > 0) {
        stats.closedCount++;
      } else {
        stats.openCount++;
      }
    }

    // Средние участники
    stats.averageMembers = groups.length > 0
      ? Math.round(stats.totalMembers / groups.length)
      : 0;

    return stats;
  }

  // ============ Sorting & Filtering Utilities ============

  /**
   * Сортирует группы по количеству участников (desc)
   */
  static sortByMembersDesc(groups: GroupApiDto[]): GroupApiDto[] {
    return [...groups].sort((a, b) => {
      const aMem = a.membersCount || 0;
      const bMem = b.membersCount || 0;
      return bMem - aMem;
    });
  }

  /**
   * Фильтрует группы по минимальному количеству участников
   */
  static filterByMinMembers(
    groups: readonly GroupApiDto[],
    minMembers: number
  ): GroupApiDto[] {
    return groups.filter((g) => (g.membersCount || 0) >= minMembers);
  }

  /**
   * Фильтрует группы по статусу
   */
  static filterByStatus(
    groups: readonly GroupApiDto[],
    status: GroupStatus
  ): GroupApiDto[] {
    return groups.filter((g) => g.status === status);
  }
}

/**
 * Утилиты для работы с mapping
 */
export class MappingUtils {
  /**
   * Безопасная конвертация snake_case → camelCase
   */
  static snakeToCamel(str: string): string {
    return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
  }

  /**
   * Безопасная конвертация camelCase → snake_case
   */
  static camelToSnake(str: string): string {
    return str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
  }

  /**
   * Конвертирует весь объект из snake_case в camelCase
   */
  static objectToCamelCase<T extends Record<string, any>>(
    obj: T
  ): Record<string, any> {
    const result: Record<string, any> = {};

    for (const [key, value] of Object.entries(obj)) {
      const camelKey = this.snakeToCamel(key);
      result[camelKey] = value;
    }

    return result;
  }

  /**
   * Конвертирует весь объект из camelCase в snake_case
   */
  static objectToSnakeCase<T extends Record<string, any>>(
    obj: T
  ): Record<string, any> {
    const result: Record<string, any> = {};

    for (const [key, value] of Object.entries(obj)) {
      const snakeKey = this.camelToSnake(key);
      result[snakeKey] = value;
    }

    return result;
  }
}
