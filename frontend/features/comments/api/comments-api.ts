/**
 * API функции для работы с комментариями
 */

import { httpClient } from "@/shared/lib/http-client";
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
  return await httpClient.get("/api/v1/comments", { params });
};

export const getComment = async (
  commentId: number,
  params: GetCommentParams = {}
): Promise<CommentResponse> => {
  return await httpClient.get(`/api/v1/comments/${commentId}`, { params });
};

export const getCommentByVkId = async (vkId: number): Promise<CommentResponse> => {
  return await httpClient.get(`/api/v1/comments/vk/${vkId}`);
};

export const createComment = async (data: CommentCreate): Promise<CommentResponse> => {
  return await httpClient.post("/api/v1/comments", data);
};

export const updateComment = async (
  commentId: number,
  data: CommentUpdate
): Promise<CommentResponse> => {
  return await httpClient.put(`/api/v1/comments/${commentId}`, data);
};

export const deleteComment = async (commentId: number): Promise<{ message: string }> => {
  return await httpClient.delete(`/api/v1/comments/${commentId}`);
};

// Статистика
export const getCommentsStats = async (): Promise<CommentStats> => {
  return await httpClient.get("/api/v1/comments/stats/overview");
};

export const getCommentsMetrics = async (): Promise<CommentsMetrics> => {
  return await httpClient.get("/api/v1/comments/metrics");
};

// Анализ ключевых слов
export const analyzeKeywords = async (
  request: KeywordAnalysisRequest
): Promise<KeywordAnalysisResponse> => {
  return await httpClient.post("/api/v1/comments/keyword-analysis/analyze", request);
};

export const analyzeBatchKeywords = async (
  request: BatchKeywordAnalysisRequest
): Promise<BatchKeywordAnalysisResponse> => {
  return await httpClient.post("/api/v1/comments/keyword-analysis/analyze-batch", request);
};

export const searchByKeywords = async (
  request: KeywordSearchRequest
): Promise<KeywordSearchResponse> => {
  return await httpClient.post("/api/v1/comments/keyword-analysis/search", request);
};

export const getKeywordStatistics = async (): Promise<KeywordStatisticsResponse> => {
  return await httpClient.get("/api/v1/comments/keyword-analysis/statistics");
};
