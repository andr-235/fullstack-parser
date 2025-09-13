/**
 * React Query хуки для работы с комментариями
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getComments,
  getComment,
  getCommentByVkId,
  createComment,
  updateComment,
  deleteComment,
  getCommentsStats,
  getCommentsMetrics,
  analyzeKeywords,
  analyzeBatchKeywords,
  searchByKeywords,
  getKeywordStatistics,
} from "./comments-api";
import type {
  GetCommentsParams,
  GetCommentParams,
  CommentCreate,
  CommentUpdate,
  KeywordAnalysisRequest,
  BatchKeywordAnalysisRequest,
  KeywordSearchRequest,
} from "../model/types";

// Query keys
export const commentsKeys = {
  all: ["comments"] as const,
  lists: () => [...commentsKeys.all, "list"] as const,
  list: (params: GetCommentsParams) => [...commentsKeys.lists(), params] as const,
  details: () => [...commentsKeys.all, "detail"] as const,
  detail: (id: number) => [...commentsKeys.details(), id] as const,
  vkDetail: (vkId: number) => [...commentsKeys.details(), "vk", vkId] as const,
  stats: () => [...commentsKeys.all, "stats"] as const,
  metrics: () => [...commentsKeys.all, "metrics"] as const,
  keywordAnalysis: () => [...commentsKeys.all, "keyword-analysis"] as const,
  keywordStats: () => [...commentsKeys.keywordAnalysis(), "statistics"] as const,
};

// Хуки для получения данных
export const useComments = (params: GetCommentsParams = {}) => {
  return useQuery({
    queryKey: commentsKeys.list(params),
    queryFn: () => getComments(params),
    staleTime: 5 * 60 * 1000, // 5 минут
  });
};

export const useComment = (commentId: number, params: GetCommentParams = {}) => {
  return useQuery({
    queryKey: commentsKeys.detail(commentId),
    queryFn: () => getComment(commentId, params),
    enabled: !!commentId,
  });
};

export const useCommentByVkId = (vkId: number) => {
  return useQuery({
    queryKey: commentsKeys.vkDetail(vkId),
    queryFn: () => getCommentByVkId(vkId),
    enabled: !!vkId,
  });
};

export const useCommentsStats = () => {
  return useQuery({
    queryKey: commentsKeys.stats(),
    queryFn: getCommentsStats,
    staleTime: 10 * 60 * 1000, // 10 минут
  });
};

export const useCommentsMetrics = () => {
  return useQuery({
    queryKey: commentsKeys.metrics(),
    queryFn: getCommentsMetrics,
    staleTime: 5 * 60 * 1000, // 5 минут
  });
};

export const useKeywordStatistics = () => {
  return useQuery({
    queryKey: commentsKeys.keywordStats(),
    queryFn: getKeywordStatistics,
    staleTime: 15 * 60 * 1000, // 15 минут
  });
};

// Мутации
export const useCreateComment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createComment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: commentsKeys.lists() });
      queryClient.invalidateQueries({ queryKey: commentsKeys.stats() });
      queryClient.invalidateQueries({ queryKey: commentsKeys.metrics() });
    },
  });
};

export const useUpdateComment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ commentId, data }: { commentId: number; data: CommentUpdate }) =>
      updateComment(commentId, data),
    onSuccess: (_, { commentId }) => {
      queryClient.invalidateQueries({ queryKey: commentsKeys.detail(commentId) });
      queryClient.invalidateQueries({ queryKey: commentsKeys.lists() });
    },
  });
};

export const useDeleteComment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteComment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: commentsKeys.lists() });
      queryClient.invalidateQueries({ queryKey: commentsKeys.stats() });
      queryClient.invalidateQueries({ queryKey: commentsKeys.metrics() });
    },
  });
};

// Анализ ключевых слов
export const useAnalyzeKeywords = () => {
  return useMutation({
    mutationFn: analyzeKeywords,
  });
};

export const useAnalyzeBatchKeywords = () => {
  return useMutation({
    mutationFn: analyzeBatchKeywords,
  });
};

export const useSearchByKeywords = () => {
  return useMutation({
    mutationFn: searchByKeywords,
  });
};
