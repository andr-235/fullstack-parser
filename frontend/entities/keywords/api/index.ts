import type { Keyword, CreateKeywordRequest, UpdateKeywordRequest, KeywordsFilters } from '../types';

// Базовый URL API - можно вынести в конфиг
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost';

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface KeywordsResponse {
  data: Keyword[];
  total: number;
  page: number;
  limit: number;
}

class KeywordsApi {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    maxRetries: number = 3
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    let lastError: Error;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const response = await fetch(url, config);

        if (!response.ok) {
          // Для 503 ошибки делаем retry
          if (response.status === 503 && attempt < maxRetries) {
            const delay = Math.pow(2, attempt) * 1000; // Экспоненциальная задержка: 1s, 2s, 4s
            await new Promise(resolve => setTimeout(resolve, delay));
            continue;
          }

          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
      } catch (error) {
        lastError = error instanceof Error ? error : new Error('Network error occurred');

        // Для сетевых ошибок также делаем retry, кроме последней попытки
        if (attempt < maxRetries && !(error instanceof Error && error.message.includes('HTTP'))) {
          const delay = Math.pow(2, attempt) * 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
          continue;
        }

        break;
      }
    }

    throw lastError!;
  }

  /**
   * Получить список ключевых слов с фильтрами
   */
  async getKeywords(filters: KeywordsFilters = {}): Promise<Keyword[]> {
    const params = new URLSearchParams();

    if (filters.search) params.append('search', filters.search);
    if (filters.category) params.append('category', filters.category);
    if (filters.active_only !== undefined) params.append('active_only', filters.active_only.toString());
    if (filters.limit) params.append('limit', filters.limit.toString());

    const queryString = params.toString();
    const endpoint = `/api/v1/keywords${queryString ? `?${queryString}` : ''}`;

    const response = await this.request<Keyword[]>(endpoint);
    return response;
  }

  /**
   * Получить ключевое слово по ID
   */
  async getKeyword(id: number): Promise<Keyword> {
    const response = await this.request<Keyword>(`/api/v1/keywords/${id}`);
    return response;
  }

  /**
   * Создать новое ключевое слово
   */
  async createKeyword(request: CreateKeywordRequest): Promise<Keyword> {
    const response = await this.request<Keyword>('/api/v1/keywords', {
      method: 'POST',
      body: JSON.stringify({
        word: request.word,
        description: request.description,
        category_name: request.category_name,
        priority: request.priority,
      }),
    });

    // Преобразовать ответ backend в формат frontend
    return {
      word: response.word,
      is_active: response.is_active,
      ...(response.category_name !== undefined && { category_name: response.category_name }),
      id: response.id,
      name: response.word,
      frequency: 0, // Backend не возвращает frequency, устанавливаем 0
      created_at: response.created_at,
      updated_at: response.created_at, // Используем created_at как updated_at
      status: { is_active: response.is_active },
      ...(response.category_name && { category: { name: response.category_name } }),
      ...(response.description !== undefined && { description: response.description }),
      match_count: response.match_count || 0,
    };
  }

  /**
   * Обновить ключевое слово
   */
  async updateKeyword(id: number, request: UpdateKeywordRequest): Promise<Keyword> {
    const updateData: Partial<{
      word: string;
      description: string;
      category_name: string;
      priority: number;
    }> = {};

    if (request.word !== undefined) updateData.word = request.word;
    if (request.description !== undefined) updateData.description = request.description;
    if (request.category_name !== undefined) updateData.category_name = request.category_name;
    if (request.priority !== undefined) updateData.priority = request.priority;

    const response = await this.request<{ message: string }>(`/api/v1/keywords/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });

    // После обновления получаем актуальные данные
    return await this.getKeyword(id);
  }

  /**
   * Удалить ключевое слово
   */
  async deleteKeyword(id: number): Promise<void> {
    await this.request(`/api/v1/keywords/${id}`, {
      method: 'DELETE',
    });
  }

  /**
   * Активировать ключевое слово
   */
  async activateKeyword(id: number): Promise<Keyword> {
    await this.request<{ message: string }>(`/api/v1/keywords/${id}/activate`, {
      method: 'PATCH',
    });

    return await this.getKeyword(id);
  }

  /**
   * Деактивировать ключевое слово
   */
  async deactivateKeyword(id: number): Promise<Keyword> {
    await this.request<{ message: string }>(`/api/v1/keywords/${id}/deactivate`, {
      method: 'PATCH',
    });

    return await this.getKeyword(id);
  }

  /**
   * Переключить статус ключевого слова (активно/неактивно)
   */
  async toggleKeywordStatus(id: number, isActive: boolean): Promise<Keyword> {
    if (isActive) {
      return await this.activateKeyword(id);
    } else {
      return await this.deactivateKeyword(id);
    }
  }
}

export const keywordsApi = new KeywordsApi();