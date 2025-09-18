import { create } from 'zustand';
import { commentApi } from './api';
import type {
  Comment,
  CommentCreateRequest,
  CommentUpdateRequest,
  CommentListResponse,
  CommentFilters
} from './types';

interface CommentState {
  comments: Comment[];
  currentComment: Comment | null;
  isLoading: boolean;
  error: string | null;
  total: number;

  // Actions
  fetchComments: (filters?: CommentFilters) => Promise<void>;
  fetchCommentById: (id: string) => Promise<void>;
  createComment: (data: CommentCreateRequest) => Promise<Comment>;
  updateComment: (id: string, data: CommentUpdateRequest) => Promise<Comment>;
  deleteComment: (id: string) => Promise<void>;
  fetchPostComments: (postId: string, limit?: number, offset?: number) => Promise<void>;
  fetchCommentReplies: (commentId: string, limit?: number, offset?: number) => Promise<void>;
  clearError: () => void;
  setCurrentComment: (comment: Comment | null) => void;
}

export const useCommentStore = create<CommentState>((set, get) => ({
  comments: [],
  currentComment: null,
  isLoading: false,
  error: null,
  total: 0,

  fetchComments: async (filters = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response: CommentListResponse = await commentApi.getComments(filters);
      set({
        comments: response.comments,
        total: response.total,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка загрузки комментариев';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  fetchCommentById: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const comment: Comment = await commentApi.getCommentById(id);
      set({
        currentComment: comment,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка загрузки комментария';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  createComment: async (data: CommentCreateRequest) => {
    set({ isLoading: true, error: null });
    try {
      const comment: Comment = await commentApi.createComment(data);
      const { comments } = get();
      set({
        comments: [comment, ...comments],
        isLoading: false
      });
      return comment;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка создания комментария';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  updateComment: async (id: string, data: CommentUpdateRequest) => {
    set({ isLoading: true, error: null });
    try {
      const comment: Comment = await commentApi.updateComment(id, data);
      const { comments } = get();
      const updatedComments = comments.map(c => c.id === id ? comment : c);
      set({
        comments: updatedComments,
        currentComment: comment,
        isLoading: false
      });
      return comment;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка обновления комментария';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  deleteComment: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await commentApi.deleteComment(id);
      const { comments } = get();
      const filteredComments = comments.filter(c => c.id !== id);
      set({
        comments: filteredComments,
        currentComment: null,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка удаления комментария';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  fetchPostComments: async (postId: string, limit = 50, offset = 0) => {
    set({ isLoading: true, error: null });
    try {
      const response: CommentListResponse = await commentApi.getPostComments(postId, limit, offset);
      set({
        comments: response.comments,
        total: response.total,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка загрузки комментариев поста';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  fetchCommentReplies: async (commentId: string, limit = 50, offset = 0) => {
    set({ isLoading: true, error: null });
    try {
      const response: CommentListResponse = await commentApi.getCommentReplies(commentId, limit, offset);
      set({
        comments: response.comments,
        total: response.total,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка загрузки ответов на комментарий';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },

  setCurrentComment: (comment: Comment | null) => {
    set({ currentComment: comment });
  },
}));