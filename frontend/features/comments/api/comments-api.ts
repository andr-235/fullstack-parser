/**
 * API функции для работы с комментариями
 */

import { apiClient } from "@/shared/lib/api";
import type {
  CommentResponse,
  CommentListResponse,
  CommentCreate,
  CommentUpdate,
  CommentStats,
  KeywordAnalysisRequest,
  KeywordAnalysisResponse,
  BatchKeywordAnalysisRequest,
  BatchKeywordAnalysisResponse,
  KeywordSearchRequest,
  KeywordSearchResponse,
  KeywordStatisticsResponse,
  CommentsMetrics,
  GetCommentsParams,
  GetCommentParams,
} from "../model/types";

// Базовые CRUD операции
export const getComments = async (params: GetCommentsParams = {}): Promise<CommentListResponse> => {
  const response = await apiClient.get("/comments", { params });
  return response.data;
};

export const getComment = async (
  commentId: number,
  params: GetCommentParams = {}
): Promise<CommentResponse> => {
  const response = await apiClient.get(`/comments/${commentId}`, { params });
  return response.data;
};

export const getCommentByVkId = async (vkId: number): Promise<CommentResponse> => {
  const response = await apiClient.get(`/comments/vk/${vkId}`);
  return response.data;
};

export const createComment = async (data: CommentCreate): Promise<CommentResponse> => {
  const response = await apiClient.post("/comments", data);
  return response.data;
};

export const updateComment = async (
  commentId: number,
  data: CommentUpdate
): Promise<CommentResponse> => {
  const response = await apiClient.put(`/comments/${commentId}`, data);
  return response.data;
};

export const deleteComment = async (commentId: number): Promise<{ message: string }> => {
  const response = await apiClient.delete(`/comments/${commentId}`);
  return response.data;
};

// Статистика
export const getCommentsStats = async (): Promise<CommentStats> => {
  const response = await apiClient.get("/comments/stats/overview");
  return response.data;
};

export const getCommentsMetrics = async (): Promise<CommentsMetrics> => {
  const response = await apiClient.get("/comments/metrics");
  return response.data;
};

// Анализ ключевых слов
export const analyzeKeywords = async (
  request: KeywordAnalysisRequest
): Promise<KeywordAnalysisResponse> => {
  const response = await apiClient.post("/comments/keyword-analysis/analyze", request);
  return response.data;
};

export const analyzeBatchKeywords = async (
  request: BatchKeywordAnalysisRequest
): Promise<BatchKeywordAnalysisResponse> => {
  const response = await apiClient.post("/comments/keyword-analysis/analyze-batch", request);
  return response.data;
};

export const searchByKeywords = async (
  request: KeywordSearchRequest
): Promise<KeywordSearchResponse> => {
  const response = await apiClient.post("/comments/keyword-analysis/search", request);
  return response.data;
};

export const getKeywordStatistics = async (): Promise<KeywordStatisticsResponse> => {
  const response = await apiClient.get("/comments/keyword-analysis/statistics");
  return response.data;
};
