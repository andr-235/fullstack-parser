import { apiClient } from '@/shared/api/client';
import type {
  Author,
  AuthorCreateRequest,
  AuthorUpdateRequest,
  AuthorListResponse,
  AuthorFilters
} from '../types';

export const authorApi = {
  async getAuthors(filters: AuthorFilters = {}): Promise<AuthorListResponse> {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get<AuthorListResponse>(`/authors?${params}`);
    return response.data;
  },

  async getAuthorById(id: string): Promise<Author> {
    const response = await apiClient.get<Author>(`/authors/${id}`);
    return response.data;
  },

  async createAuthor(data: AuthorCreateRequest): Promise<Author> {
    const response = await apiClient.post<Author>('/authors', data);
    return response.data;
  },

  async updateAuthor(id: string, data: AuthorUpdateRequest): Promise<Author> {
    const response = await apiClient.put<Author>(`/authors/${id}`, data);
    return response.data;
  },

  async deleteAuthor(id: string): Promise<void> {
    await apiClient.delete(`/authors/${id}`);
  },

  async getAuthorByVkId(vkId: string): Promise<Author> {
    const response = await apiClient.get<Author>(`/authors/by-vk-id/${vkId}`);
    return response.data;
  },

  async searchAuthors(query: string, limit = 20): Promise<AuthorListResponse> {
    const response = await apiClient.get<AuthorListResponse>(
      `/authors?search=${encodeURIComponent(query)}&limit=${limit}`
    );
    return response.data;
  },
};