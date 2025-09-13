/**
 * API функции для sidebar
 */

import { httpClient } from "@/shared/lib/http-client";
import type { SidebarData, SidebarStats, User, Team, Project } from "../model/types";

export const sidebarApi = {
  /**
   * Получить статистику для sidebar
   */
  async getStats(): Promise<SidebarStats> {
    return httpClient.get<SidebarStats>("/api/v1/sidebar/stats");
  },

  /**
   * Получить данные пользователя
   */
  async getUser(): Promise<User> {
    return httpClient.get<User>("/api/v1/user/profile");
  },

  /**
   * Получить команды пользователя
   */
  async getTeams(): Promise<Team[]> {
    return httpClient.get<Team[]>("/api/v1/user/teams");
  },

  /**
   * Получить проекты пользователя
   */
  async getProjects(): Promise<Project[]> {
    return httpClient.get<Project[]>("/api/v1/user/projects");
  },

  /**
   * Обновить профиль пользователя
   */
  async updateUserProfile(data: {
    name?: string;
    email?: string;
    avatar?: string;
  }): Promise<User> {
    return httpClient.patch<User>("/api/v1/user/profile", data);
  },

  /**
   * Переключить команду
   */
  async switchTeam(teamId: string): Promise<void> {
    return httpClient.post<void>("/api/v1/user/switch-team", { teamId });
  },

  /**
   * Создать проект
   */
  async createProject(data: {
    name: string;
    description?: string;
  }): Promise<Project> {
    return httpClient.post<Project>("/api/v1/projects", data);
  },

  /**
   * Удалить проект
   */
  async deleteProject(projectId: string): Promise<void> {
    return httpClient.delete<void>(`/api/v1/projects/${projectId}`);
  },
};

// Экспорт для обратной совместимости
export const fetchSidebarStats = sidebarApi.getStats;
export const updateUserProfile = sidebarApi.updateUserProfile;
export const switchTeam = sidebarApi.switchTeam;
export const createProject = sidebarApi.createProject;
export const deleteProject = sidebarApi.deleteProject;
