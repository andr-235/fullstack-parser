"use client";

import { useEffect, useMemo } from "react";
import {
  GalleryVerticalEnd,
  LayoutDashboard,
  MessageSquare,
  Users,
  Hash,
  Monitor,
  FileText,
  Settings,
} from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { useNavigation } from "@/shared/contexts/NavigationContext";
import { useSidebarStore } from "./sidebar-store";
import type { SidebarData, SidebarStats } from "./types";

/**
 * Хук для работы с данными sidebar
 */
export const useSidebarData = (): SidebarData => {
  const { data, isLoading, error, fetchData } = useSidebarStore();
  const { stats, activePath } = useNavigation();

  // Загружаем данные при монтировании
  useEffect(() => {
    if (!data && !isLoading) {
      fetchData().catch(() => {
        // Ошибка обрабатывается в store
      });
    }
  }, [data, isLoading, fetchData]);

  // Fallback данные для случаев ошибки или загрузки
  const fallbackData: SidebarData = useMemo(
    () => ({
      user: {
        id: "1",
        name: "Администратор",
        email: "admin@vkparser.com",
        avatar: "/avatars/admin.svg",
        role: "admin" as const,
        status: "active" as const,
      },
      teams: [
        {
          id: "1",
          name: "Парсер комментариев VK",
          logo: GalleryVerticalEnd,
          plan: "Корпоративная",
          status: "active" as const,
        },
      ],
      projects: [
        {
          id: "1",
          name: "Мониторинг",
          url: "/monitoring",
          icon: Monitor,
          status: "active" as const,
          description: "Мониторинг активности групп",
        },
        {
          id: "2",
          name: "Парсер",
          url: "/parser",
          icon: FileText,
          status: "active" as const,
          description: "Парсинг комментариев",
        },
        {
          id: "3",
          name: "Настройки",
          url: "/settings",
          icon: Settings,
          status: "active" as const,
          description: "Настройки системы",
        },
      ],
      navItems: [],
      stats: {
        comments: { new: 0, total: 0 },
        groups: { active: 0, total: 0 },
        keywords: { active: 0, total: 0 },
      },
    }),
    []
  );

  // Используем данные из store или fallback
  const currentData = data || fallbackData;

  // Обновляем навигационные элементы с актуальными данными
  const navItems = useMemo(() => {
    const statsData: SidebarStats = stats || currentData.stats;

    return [
      {
        id: "dashboard",
        title: "Панель управления",
        url: "/dashboard",
        icon: LayoutDashboard,
        isActive: activePath === "/dashboard",
      },
      {
        id: "comments",
        title: "Комментарии",
        url: "/comments",
        icon: MessageSquare,
        isActive: activePath === "/comments",
        badge: statsData.comments.new ? (
          <Badge variant="destructive" className="ml-auto">
            {statsData.comments.new}
          </Badge>
        ) : undefined,
      },
      {
        id: "groups",
        title: "Группы",
        url: "/groups",
        icon: Users,
        isActive: activePath === "/groups",
        badge: statsData.groups.active ? (
          <Badge variant="secondary" className="ml-auto">
            {statsData.groups.active}
          </Badge>
        ) : undefined,
      },
      {
        id: "keywords",
        title: "Ключевые слова",
        url: "/keywords",
        icon: Hash,
        isActive: activePath === "/keywords",
        badge: statsData.keywords.active ? (
          <Badge variant="outline" className="ml-auto">
            {statsData.keywords.active}
          </Badge>
        ) : undefined,
      },
    ];
  }, [stats, activePath, currentData.stats]);

  return {
    ...currentData,
    navItems,
    stats: stats || currentData.stats,
  };
};
