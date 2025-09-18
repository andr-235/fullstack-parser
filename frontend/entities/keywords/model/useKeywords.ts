import { useState, useEffect, useCallback } from 'react';
import type { Keyword, CreateKeywordRequest, UpdateKeywordRequest } from '../types';
import { keywordsApi } from '../api';

interface UseKeywordsOptions {
  category?: string;
  limit?: number;
}

export const useKeywords = (options: UseKeywordsOptions = {}) => {
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchKeywords = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const filters: any = {
        active_only: true,
      };

      if (options.limit) filters.limit = options.limit;
      if (options.category) filters.category = options.category;

      const keywordsData = await keywordsApi.getKeywords(filters);
      setKeywords(keywordsData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch keywords');
    } finally {
      setLoading(false);
    }
  }, [options.limit, options.category]);

  const refetch = useCallback(() => {
    fetchKeywords();
  }, [fetchKeywords]);

  const createKeyword = useCallback(async (request: CreateKeywordRequest): Promise<Keyword> => {
    try {
      setError(null);
      const newKeyword = await keywordsApi.createKeyword(request);
      setKeywords(prev => [...prev, newKeyword]);
      return newKeyword;
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to create keyword';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const updateKeyword = useCallback(async (id: number, request: UpdateKeywordRequest): Promise<Keyword> => {
    try {
      setError(null);
      const updatedKeyword = await keywordsApi.updateKeyword(id, request);
      setKeywords(prev => prev.map(k => k.id === id ? updatedKeyword : k));
      return updatedKeyword;
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to update keyword';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const deleteKeyword = useCallback(async (id: number): Promise<void> => {
    try {
      setError(null);
      await keywordsApi.deleteKeyword(id);
      setKeywords(prev => prev.filter(k => k.id !== id));
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to delete keyword';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const toggleKeywordStatus = useCallback(async (id: number, isActive: boolean): Promise<Keyword> => {
    try {
      setError(null);
      const updatedKeyword = await keywordsApi.toggleKeywordStatus(id, isActive);
      setKeywords(prev => prev.map(k => k.id === id ? updatedKeyword : k));
      return updatedKeyword;
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to toggle keyword status';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  useEffect(() => {
    fetchKeywords();
  }, []);

  return {
    keywords,
    loading,
    error,
    refetch,
    createKeyword,
    updateKeyword,
    deleteKeyword,
    toggleKeywordStatus,
  };
};
