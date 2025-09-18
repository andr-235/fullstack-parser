import { apiClient } from '@/shared/api/client';
import type {
  Comment,
  CommentCreateRequest,
  CommentUpdateRequest,
  CommentListResponse,
  CommentFilters
} from '../types';

export const commentApi = {
  async getComments(filters: CommentFilters = {}): Promise<CommentListResponse> {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get<CommentListResponse>(`/comments?${params}`);
    return response.data;
  },

  async getCommentById(id: string): Promise<Comment> {
    const response = await apiClient.get<Comment>(`/comments/${id}`);
    return response.data;
  },

  async createComment(data: CommentCreateRequest): Promise<Comment> {
    const response = await apiClient.post<Comment>('/comments', data);
    return response.data;
  },

  async updateComment(id: string, data: CommentUpdateRequest): Promise<Comment> {
    const response = await apiClient.put<Comment>(`/comments/${id}`, data);
    return response.data;
  },

  async deleteComment(id: string): Promise<void> {
    await apiClient.delete(`/comments/${id}`);
  },

  async getPostComments(postId: string, limit = 50, offset = 0): Promise<CommentListResponse> {
    const response = await apiClient.get<CommentListResponse>(
      `/comments?post_id=${postId}&limit=${limit}&offset=${offset}`
    );
    return response.data;
  },

  async getCommentReplies(commentId: string, limit = 50, offset = 0): Promise<CommentListResponse> {
    const response = await apiClient.get<CommentListResponse>(
      `/comments?parent_id=${commentId}&limit=${limit}&offset=${offset}`
    );
    return response.data;
  },
};