/**
 * @fileoverview Domain types для Groups module
 *
 * ПРАВИЛО: Single Source of Truth
 * НИКОГДА не дублировать эти типы в других файлах!
 *
 * Слои трансформации данных:
 * 1. VK API Layer (snake_case) - как приходит от VK API
 * 2. Parsing Layer (intermediate) - промежуточный формат из файла
 * 3. Database Layer (snake_case) - как хранится в PostgreSQL
 * 4. API Layer (camelCase) - как отдается frontend
 * 5. Business Logic Layer - для внутренней бизнес-логики
 */

import { groups as PrismaGroup, GroupStatus } from '@prisma/client';

// ============ VK API Layer (snake_case) ============

/**
 * Данные группы от VK API (метод groups.getById)
 * Используется: VkIoService.getGroupsInfo()
 *
 * @see https://dev.vk.com/method/groups.getById
 */
export interface VkGroupRaw {
  readonly id: number;
  readonly name: string;
  readonly screen_name: string;
  readonly description: string | null;
  readonly photo_50: string | null;
  readonly members_count: number;
  readonly is_closed: 0 | 1 | 2; // 0 = открытая, 1 = закрытая, 2 = приватная
}

// ============ Parsing Layer (intermediate) ============

/**
 * Результат парсинга одной строки из файла
 * Используется: FileParser.parseGroupsFile()
 *
 * Может содержать либо ID, либо screen_name, либо оба
 */
export interface ParsedGroupInput {
  readonly id?: number;
  readonly name: string;
  readonly screenName?: string;
  readonly url?: string;
  readonly rawLine?: string; // Оригинальная строка для отладки
}

// ============ Database Layer (snake_case) ============

/**
 * Тип из Prisma - как хранится в PostgreSQL
 * Re-export для удобства импорта
 */
export type DbGroup = PrismaGroup;

/**
 * Данные для создания группы в БД
 * Используется: GroupsRepository.createGroups()
 */
export interface CreateGroupInput {
  readonly vk_id: number;
  readonly name: string;
  readonly screen_name: string | null;
  readonly photo_50: string | null;
  readonly members_count: number | null;
  readonly is_closed: number;
  readonly description: string | null;
  readonly status: GroupStatus;
  readonly task_id: string;
}

// ============ API Layer (camelCase) ============

/**
 * DTO для API ответа фронтенду
 * Используется: GroupsController, API responses
 *
 * Все поля в camelCase согласно JavaScript conventions
 */
export interface GroupApiDto {
  readonly id: number;
  readonly vkId: number;
  readonly name: string;
  readonly screenName: string | null;
  readonly photo50: string | null;
  readonly membersCount: number | null;
  readonly isClosed: number;
  readonly description: string | null;
  readonly status: GroupStatus;
  readonly uploadedAt: Date;
  readonly taskId: string | null;
}

// ============ Business Logic Layer ============

/**
 * Результат валидации группы через VK API
 */
export interface GroupValidationResult {
  readonly isValid: boolean;
  readonly vkId: number;
  readonly errors: readonly string[];
  readonly vkData?: VkGroupRaw;
}

/**
 * Статус задачи загрузки групп
 * Хранится в Redis через TaskStorageService
 *
 * @example
 * const task: GroupUploadTask = {
 *   taskId: '123e4567-e89b-12d3-a456-426614174000',
 *   status: 'processing',
 *   progress: { total: 100, processed: 50, valid: 45, invalid: 5, duplicates: 0 },
 *   errors: [],
 *   createdAt: new Date(),
 *   startedAt: new Date(),
 *   completedAt: null
 * };
 */
export interface GroupUploadTask {
  readonly taskId: string;
  readonly status: 'pending' | 'processing' | 'completed' | 'failed';
  readonly progress: {
    readonly total: number;
    readonly processed: number;
    readonly valid: number;
    readonly invalid: number;
    readonly duplicates: number;
  };
  readonly errors: readonly string[];
  readonly createdAt: Date;
  readonly startedAt: Date | null;
  readonly completedAt: Date | null;
  readonly failureReason?: string;
}

/**
 * Результат операции загрузки групп
 */
export interface UploadGroupsResult {
  readonly taskId: string;
}

/**
 * Параметры получения списка групп
 * Используется после валидации через GetGroupsQuerySchema
 */
export interface GetGroupsParams {
  readonly limit: number;
  readonly offset: number;
  readonly status: 'all' | GroupStatus;
  readonly search?: string;
  readonly sortBy: 'uploaded_at' | 'name' | 'members_count' | 'status';
  readonly sortOrder: 'asc' | 'desc';
}

/**
 * Результат получения списка групп
 */
export interface GetGroupsResult {
  readonly groups: readonly GroupApiDto[];
  readonly total: number;
  readonly pagination: {
    readonly limit: number;
    readonly offset: number;
    readonly hasMore: boolean;
  };
}

/**
 * Статистика по группам
 */
export interface GroupsStats {
  readonly total: number;
  readonly valid: number;
  readonly invalid: number;
  readonly duplicate: number;
}

/**
 * Результат операции удаления групп
 */
export interface DeleteGroupsResult {
  readonly deletedCount: number;
  readonly message: string;
}

// ============ Type Guards ============

/**
 * Type guard для проверки валидного VK ID
 */
export function isValidVkId(value: unknown): value is number {
  return (
    typeof value === 'number' &&
    Number.isInteger(value) &&
    value > 0 &&
    value < 1_000_000_000
  );
}

/**
 * Type guard для проверки валидного screen_name
 */
export function isValidScreenName(value: unknown): value is string {
  if (typeof value !== 'string') return false;

  // VK screen_name правила:
  // - Только латинские буквы, цифры, подчеркивание
  // - 5-32 символа
  // - Не может начинаться с цифры
  const screenNameRegex = /^[a-zA-Z][a-zA-Z0-9_]{4,31}$/;
  return screenNameRegex.test(value);
}

/**
 * Type guard для GroupUploadTask
 */
export function isGroupUploadTask(value: unknown): value is GroupUploadTask {
  if (!value || typeof value !== 'object') return false;

  const task = value as any;

  return (
    typeof task.taskId === 'string' &&
    ['pending', 'processing', 'completed', 'failed'].includes(task.status) &&
    typeof task.progress === 'object' &&
    task.createdAt instanceof Date
  );
}
