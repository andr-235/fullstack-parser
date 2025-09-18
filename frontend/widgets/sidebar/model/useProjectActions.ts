"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { toast } from "react-hot-toast";
import { useSidebarStore } from "./sidebar-store";

/**
 * Хук для действий с проектами в sidebar
 */
export const useProjectActions = () => {
  const router = useRouter();
  const { createProject, deleteProject, isLoading, error } = useSidebarStore();

  const handleViewProject = useCallback((projectId: string) => {
    router.push(`/projects/${projectId}`);
  }, [router]);

  const handleShareProject = useCallback((projectId: string) => {
    // TODO: Implement project sharing logic
    toast(`Поделиться проектом ${projectId}`);
  }, []);

  /**
   * Асинхронная функция для удаления проекта.
   * Вызывает API для удаления проекта, показывает уведомление об успехе или ошибке.
   *
   * @param {string} projectId - Идентификатор проекта для удаления
   * @returns {Promise<void>} Не возвращает значение
   */
  const handleDeleteProject = useCallback(async (projectId: string) => {
    try {
      await deleteProject(projectId);
      toast.success(`Проект ${projectId} удален`);
    } catch (error: any) {
      console.error("Delete project error:", error);
      toast.error(error.message || "Ошибка при удалении проекта");
    }
  }, [deleteProject]);

  /**
   * Асинхронная функция для создания нового проекта.
   * Вызывает API для создания проекта с переданными данными, показывает уведомление об успехе
   * и перенаправляет на страницу проектов. В случае ошибки логирует её и показывает уведомление.
   *
   * @param {Object} data - Данные для создания проекта
   * @param {string} data.name - Название проекта
   * @param {string} [data.description] - Описание проекта (опционально)
   * @returns {Promise<void>} Не возвращает значение
   */
  const handleCreateProject = useCallback(async (data: {
    name: string;
    description?: string;
  }) => {
    try {
      await createProject(data);
      toast.success("Проект успешно создан");
      router.push("/projects");
    } catch (error: any) {
      console.error("Create project error:", error);
      toast.error(error.message || "Ошибка создания проекта");
    }
  }, [createProject, router]);

  const handleEditProject = useCallback((projectId: string) => {
    router.push(`/projects/${projectId}/edit`);
  }, [router]);

  return {
    handleViewProject,
    handleShareProject,
    handleDeleteProject,
    handleCreateProject,
    handleEditProject,
    isLoading,
    error,
  };
};
