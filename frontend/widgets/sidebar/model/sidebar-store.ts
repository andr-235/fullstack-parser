/**
 * Zustand store для управления состоянием sidebar
 */

import { create } from "zustand";
import type { SidebarData, SidebarStats, User, Team, Project, NavItem } from "./types";
import { sidebarApi } from "../api";

interface SidebarState {
  // Состояние
  data: SidebarData | null;
  isLoading: boolean;
  error: string | null;

  // Действия
  fetchData: () => Promise<void>;
  updateUserProfile: (data: { name?: string; email?: string; avatar?: string }) => Promise<void>;
  switchTeam: (teamId: string) => Promise<void>;
  createProject: (data: { name: string; description?: string }) => Promise<void>;
  deleteProject: (projectId: string) => Promise<void>;
  setLoading: (loading: boolean) => void;
  clearError: () => void;
  setData: (data: SidebarData) => void;
}

export const useSidebarStore = create<SidebarState>((set, get) => ({
  // Начальное состояние
  data: null,
  isLoading: false,
  error: null,

  // Действия
  fetchData: async () => {
    set({ isLoading: true, error: null });

    try {
      const [stats, user, teams, projects] = await Promise.all([
        sidebarApi.getStats(),
        sidebarApi.getUser(),
        sidebarApi.getTeams(),
        sidebarApi.getProjects(),
      ]);

      // Создаем навигационные элементы
      const navItems: NavItem[] = [
        {
          id: "dashboard",
          title: "Панель управления",
          url: "/dashboard",
          isActive: false, // Будет обновлено в компоненте
        },
        {
          id: "comments",
          title: "Комментарии",
          url: "/comments",
          isActive: false,
        },
        {
          id: "groups",
          title: "Группы",
          url: "/groups",
          isActive: false,
        },
        {
          id: "keywords",
          title: "Ключевые слова",
          url: "/keywords",
          isActive: false,
        },
      ];

      const sidebarData: SidebarData = {
        user,
        teams,
        projects,
        navItems,
        stats,
      };

      set({
        data: sidebarData,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      set({
        error: error.message || "Ошибка загрузки данных sidebar",
        isLoading: false,
      });
      throw error;
    }
  },

  updateUserProfile: async (data) => {
    set({ isLoading: true, error: null });

    try {
      const updatedUser = await sidebarApi.updateUserProfile(data);
      
      const currentData = get().data;
      if (currentData) {
        set({
          data: { ...currentData, user: updatedUser },
          isLoading: false,
          error: null,
        });
      }
    } catch (error: any) {
      set({
        error: error.message || "Ошибка обновления профиля",
        isLoading: false,
      });
      throw error;
    }
  },

  switchTeam: async (teamId) => {
    set({ isLoading: true, error: null });

    try {
      await sidebarApi.switchTeam(teamId);
      
      // Обновляем данные после переключения команды
      await get().fetchData();
    } catch (error: any) {
      set({
        error: error.message || "Ошибка переключения команды",
        isLoading: false,
      });
      throw error;
    }
  },

  createProject: async (data) => {
    set({ isLoading: true, error: null });

    try {
      const newProject = await sidebarApi.createProject(data);
      
      const currentData = get().data;
      if (currentData) {
        set({
          data: {
            ...currentData,
            projects: [...currentData.projects, newProject],
          },
          isLoading: false,
          error: null,
        });
      }
    } catch (error: any) {
      set({
        error: error.message || "Ошибка создания проекта",
        isLoading: false,
      });
      throw error;
    }
  },

  deleteProject: async (projectId) => {
    set({ isLoading: true, error: null });

    try {
      await sidebarApi.deleteProject(projectId);
      
      const currentData = get().data;
      if (currentData) {
        set({
          data: {
            ...currentData,
            projects: currentData.projects.filter(p => p.id !== projectId),
          },
          isLoading: false,
          error: null,
        });
      }
    } catch (error: any) {
      set({
        error: error.message || "Ошибка удаления проекта",
        isLoading: false,
      });
      throw error;
    }
  },

  setLoading: (loading) => set({ isLoading: loading }),
  clearError: () => set({ error: null }),
  setData: (data) => set({ data }),
}));
