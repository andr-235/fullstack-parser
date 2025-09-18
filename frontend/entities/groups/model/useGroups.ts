import { useState, useEffect, useCallback } from 'react';
import type { Group, UpdateGroupRequest } from '../types';
import { groupsApi } from '../api';

interface UseGroupsOptions {
  active_only?: boolean;
  size?: number;
  page?: number;
}

export const useGroups = (options: UseGroupsOptions = {}, autoFetch: boolean = false) => {
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchGroups = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Mock data for now - replace with actual API call
      const mockGroups: Group[] = [
        {
          id: 1,
          vk_id: 123456,
          name: 'Test Group 1',
          screen_name: 'testgroup1',
          description: 'Test group description',
          is_active: true,
          total_comments_found: 0,
          max_posts_to_check: 100,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 2,
          vk_id: 789012,
          name: 'Test Group 2',
          screen_name: 'testgroup2',
          description: 'Another test group',
          is_active: true,
          total_comments_found: 0,
          max_posts_to_check: 100,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 3,
          vk_id: 345678,
          name: 'Inactive Group',
          screen_name: 'inactivegroup',
          description: 'Inactive test group',
          is_active: false,
          total_comments_found: 0,
          max_posts_to_check: 100,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ];

      // Apply active_only filter if specified
      const filteredGroups = options.active_only
        ? mockGroups.filter(group => group.is_active)
        : mockGroups;

      setGroups(filteredGroups);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch groups');
    } finally {
      setLoading(false);
    }
  }, [options.active_only]);

  const refetch = useCallback(() => {
    fetchGroups();
  }, [fetchGroups]);

  const createGroup = useCallback(async (data: Omit<Group, 'id' | 'created_at' | 'updated_at'>): Promise<Group> => {
    try {
      const newGroup = await groupsApi.createGroup(data);
      await refetch();
      return newGroup;
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to create group');
      throw error;
    }
  }, [refetch]);

  const updateGroup = useCallback(async (id: number, data: UpdateGroupRequest): Promise<Group> => {
    try {
      const updatedGroup = await groupsApi.updateGroup(id, data);
      await refetch();
      return updatedGroup;
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to update group');
      throw error;
    }
  }, [refetch]);

  const deleteGroup = useCallback(async (id: number): Promise<void> => {
    try {
      await groupsApi.deleteGroup(id);
      await refetch();
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to delete group');
      throw error;
    }
  }, [refetch]);

  const toggleGroupStatus = useCallback(async (id: number, isActive: boolean): Promise<Group> => {
    try {
      const updatedGroup = await groupsApi.toggleGroupStatus(id, isActive);
      await refetch();
      return updatedGroup;
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to toggle group status');
      throw error;
    }
  }, [refetch]);

  useEffect(() => {
    if (autoFetch) {
      fetchGroups();
    }
  }, [autoFetch, fetchGroups]);

  const pagination = {
    page: options.page || 1,
    size: options.size || 20,
    total: groups.length,
    pages: Math.ceil(groups.length / (options.size || 20)),
  };

  return {
    groups,
    loading,
    error,
    pagination,
    refetch,
    createGroup,
    updateGroup,
    deleteGroup,
    toggleGroupStatus,
  };
};