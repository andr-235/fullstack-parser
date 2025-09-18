import { apiClient } from '@/shared/api/client';
import type {
  Post,
  PostCreateRequest,
  PostUpdateRequest,
  PostListResponse,
  PostFilters
} from '../types';

export const postApi = {
  async getPosts(filters: PostFilters = {}): Promise<PostListResponse> {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(v => params.append(key, v));
        } else {
          params.append(key, value.toString());
        }
      }
    });

    const response = await apiClient.get<PostListResponse>(`/posts?${params}`);
    return response.data;
  },

  async getPostById(id: string): Promise<Post> {
    const response = await apiClient.get<Post>(`/posts/${id}`);
    return response.data;
  },

  async createPost(data: PostCreateRequest): Promise<Post> {
    const response = await apiClient.post<Post>('/posts', data);
    return response.data;
  },

  async updatePost(id: string, data: PostUpdateRequest): Promise<Post> {
    const response = await apiClient.put<Post>(`/posts/${id}`, data);
    return response.data;
  },

  async deletePost(id: string): Promise<void> {
    await apiClient.delete(`/posts/${id}`);
  },

  async getGroupPosts(groupId: string, limit = 50, offset = 0): Promise<PostListResponse> {
    const response = await apiClient.get<PostListResponse>(
      `/posts?group_id=${groupId}&limit=${limit}&offset=${offset}`
    );
    return response.data;
  },

  async getUserPosts(userId: string, limit = 50, offset = 0): Promise<PostListResponse> {
    const response = await apiClient.get<PostListResponse>(
      `/posts?author_id=${userId}&limit=${limit}&offset=${offset}`
    );
    return response.data;
  },
};