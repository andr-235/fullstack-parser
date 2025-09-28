import axios, { AxiosResponse } from 'axios';
import logger from './logger';
import { VkGroup, VkApiResponse, VkApiError } from '@/types/vk';
import { ProcessedGroup, RateLimitInfo } from '@/types/common';

interface ValidationResult {
  validGroups: ProcessedGroup[];
  invalidGroups: ProcessedGroup[];
  errors: ValidationError[];
}

interface ValidationError {
  batch?: number;
  error: string;
  groups?: number[];
}

interface BatchResult {
  valid: ProcessedGroup[];
  invalid: ProcessedGroup[];
  errors: ValidationError[];
}

interface VkValidatorOptions {
  accessToken: string;
  rateLimit?: number;
  batchSize?: number;
  timeout?: number;
  apiVersion?: string;
}

class VKValidator {
  private accessToken: string;
  private baseURL = 'https://api.vk.com/method';
  private rateLimit: number;
  private lastRequestTime = 0;
  private batchSize: number;
  private timeout: number;
  private apiVersion: string;

  constructor(options: VkValidatorOptions) {
    const {
      accessToken,
      rateLimit = 3,
      batchSize = 10,
      timeout = 10000,
      apiVersion = '5.199'
    } = options;

    this.accessToken = accessToken;
    this.rateLimit = rateLimit;
    this.batchSize = batchSize;
    this.timeout = timeout;
    this.apiVersion = apiVersion;
  }

  /**
   * Валидирует группы через VK API
   */
  async validateGroups(groups: ProcessedGroup[]): Promise<ValidationResult> {
    const validGroups: ProcessedGroup[] = [];
    const invalidGroups: ProcessedGroup[] = [];
    const errors: ValidationError[] = [];

    // Фильтруем только группы с ID (отрицательные числа)
    const groupsWithId = groups.filter(group => group.id && group.id < 0);

    if (groupsWithId.length === 0) {
      return {
        validGroups: groups.filter(group => !group.id), // Группы только с именами
        invalidGroups: [],
        errors: []
      };
    }

    // Обрабатываем группы батчами
    for (let i = 0; i < groupsWithId.length; i += this.batchSize) {
      const batch = groupsWithId.slice(i, i + this.batchSize);
      const batchNumber = Math.floor(i / this.batchSize) + 1;
      const totalBatches = Math.ceil(groupsWithId.length / this.batchSize);

      try {
        await this.rateLimitDelay();
        const batchResult = await this.validateBatch(batch);

        validGroups.push(...batchResult.valid);
        invalidGroups.push(...batchResult.invalid);
        errors.push(...batchResult.errors);

        logger.info('Batch validated', {
          batch: batchNumber,
          total: totalBatches,
          valid: batchResult.valid.length,
          invalid: batchResult.invalid.length
        });
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        logger.error('Batch validation failed', {
          batch: batchNumber,
          error: errorMsg
        });

        // Помечаем все группы в батче как невалидные
        batch.forEach(group => {
          invalidGroups.push({
            ...group,
            error: 'VK API error'
          });
        });

        errors.push({
          batch: batchNumber,
          error: errorMsg,
          groups: batch.map(g => g.id!).filter(Boolean)
        });
      }
    }

    // Добавляем группы только с именами как валидные
    const nameOnlyGroups = groups.filter(group => !group.id);
    validGroups.push(...nameOnlyGroups);

    return {
      validGroups,
      invalidGroups,
      errors
    };
  }

  /**
   * Валидирует батч групп через VK API
   */
  private async validateBatch(batch: ProcessedGroup[]): Promise<BatchResult> {
    const groupIds = batch
      .map(group => Math.abs(group.id!))
      .filter(Boolean)
      .join(',');

    const response: AxiosResponse<VkApiResponse<VkGroup[]> | VkApiError> = await axios.get(
      `${this.baseURL}/groups.getById`,
      {
        params: {
          group_ids: groupIds,
          access_token: this.accessToken,
          v: this.apiVersion,
          fields: 'name,screen_name,type,is_closed,photo_50,photo_100,photo_200,description,members_count'
        },
        timeout: this.timeout
      }
    );

    if ('error' in response.data) {
      throw new Error(`VK API error: ${(response.data as any).error_msg || 'Unknown error'}`);
    }

    const validGroups: ProcessedGroup[] = [];
    const invalidGroups: ProcessedGroup[] = [];
    const errors: ValidationError[] = [];

    const apiResponse = response.data as VkApiResponse<VkGroup[]>;
    const validGroupIds = new Set(
      apiResponse.response.map(group => -group.id)
    );

    batch.forEach(group => {
      if (group.id && validGroupIds.has(group.id)) {
        const vkGroup = apiResponse.response.find(g => -g.id === group.id);
        if (vkGroup) {
          validGroups.push({
            id: group.id,
            name: vkGroup.name || group.name,
            url: `https://vk.com/${vkGroup.screen_name}`
          });
        }
      } else {
        invalidGroups.push({
          ...group,
          error: 'Group not found'
        });
      }
    });

    return {
      valid: validGroups,
      invalid: invalidGroups,
      errors
    };
  }

  /**
   * Задержка для соблюдения rate limit
   */
  private async rateLimitDelay(): Promise<void> {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;
    const minInterval = 1000 / this.rateLimit;

    if (timeSinceLastRequest < minInterval) {
      const delay = minInterval - timeSinceLastRequest;
      await new Promise(resolve => setTimeout(resolve, delay));
    }

    this.lastRequestTime = Date.now();
  }

  /**
   * Проверяет доступность VK API
   */
  async checkApiHealth(): Promise<boolean> {
    try {
      await this.rateLimitDelay();
      const response: AxiosResponse<VkApiResponse<any[]> | VkApiError> = await axios.get(
        `${this.baseURL}/users.get`,
        {
          params: {
            access_token: this.accessToken,
            v: this.apiVersion
          },
          timeout: 5000
        }
      );

      return !('error' in response.data);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('VK API health check failed', { error: errorMsg });
      return false;
    }
  }

  /**
   * Получает информацию о rate limit
   */
  getRateLimitInfo(): RateLimitInfo {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;
    const minInterval = 1000 / this.rateLimit;
    const remaining = Math.max(0, Math.ceil((minInterval - timeSinceLastRequest) / 1000));

    return {
      limit: this.rateLimit,
      remaining,
      reset: new Date(now + (remaining * 1000))
    };
  }

  /**
   * Устанавливает новый токен доступа
   */
  setAccessToken(token: string): void {
    this.accessToken = token;
  }

  /**
   * Получает текущие настройки валидатора
   */
  getSettings(): VkValidatorOptions {
    return {
      accessToken: this.accessToken,
      rateLimit: this.rateLimit,
      batchSize: this.batchSize,
      timeout: this.timeout,
      apiVersion: this.apiVersion
    };
  }
}

export default VKValidator;
export { VKValidator };
export type { ValidationResult, ValidationError, VkValidatorOptions };