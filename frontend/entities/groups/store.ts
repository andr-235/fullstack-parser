import { create } from 'zustand';
import { groupsApi } from './api';
import type { Group, UpdateGroupRequest } from './types';

interface GroupsState {
  groups: Group[];
  currentGroup: Group | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchGroups: () => Promise<void>;
  fetchGroupById: (id: number) => Promise<void>;
  createGroup: (data: Omit<Group, 'id' | 'created_at' | 'updated_at'>) => Promise<Group>;
  updateGroup: (id: number, data: UpdateGroupRequest) => Promise<Group>;
  deleteGroup: (id: number) => Promise<void>;
  toggleGroupStatus: (id: number, isActive: boolean) => Promise<Group>;
  clearError: () => void;
  setCurrentGroup: (group: Group | null) => void;
}

export const useGroupsStore = create<GroupsState>((set, get) => ({
  groups: [],
  currentGroup: null,
  isLoading: false,
  error: null,

  fetchGroups: async () => {
    set({ isLoading: true, error: null });
    try {
      // Note: API doesn't have getGroups method, so we'll need to implement it or use existing data
      // For now, this is a placeholder - groups might be fetched from other sources
      set({ isLoading: false });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка загрузки групп';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  fetchGroupById: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      // Note: API doesn't have getGroupById method, so we'll need to implement it
      // For now, this is a placeholder
      set({ isLoading: false });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка загрузки группы';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  createGroup: async (data: Omit<Group, 'id' | 'created_at' | 'updated_at'>) => {
    set({ isLoading: true, error: null });
    try {
      const group: Group = await groupsApi.createGroup(data);
      const { groups } = get();
      set({
        groups: [group, ...groups],
        isLoading: false
      });
      return group;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка создания группы';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  updateGroup: async (id: number, data: UpdateGroupRequest) => {
    set({ isLoading: true, error: null });
    try {
      const group: Group = await groupsApi.updateGroup(id, data);
      const { groups } = get();
      const updatedGroups = groups.map(g => g.id === id ? group : g);
      set({
        groups: updatedGroups,
        currentGroup: group,
        isLoading: false
      });
      return group;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка обновления группы';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  deleteGroup: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await groupsApi.deleteGroup(id);
      const { groups } = get();
      const filteredGroups = groups.filter(g => g.id !== id);
      set({
        groups: filteredGroups,
        currentGroup: null,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка удаления группы';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  toggleGroupStatus: async (id: number, isActive: boolean) => {
    set({ isLoading: true, error: null });
    try {
      const group: Group = await groupsApi.toggleGroupStatus(id, isActive);
      const { groups } = get();
      const updatedGroups = groups.map(g => g.id === id ? group : g);
      set({
        groups: updatedGroups,
        currentGroup: group,
        isLoading: false
      });
      return group;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка изменения статуса группы';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },

  setCurrentGroup: (group: Group | null) => {
    set({ currentGroup: group });
  },
}));