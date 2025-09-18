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
  User,
  LogOut,
} from "lucide-react";
import { Badge } from "../ui/custom/Badge";
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
  }, [data, isLoading]); // Убрали fetchData из зависимостей

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

  // Конфигурация навигационных элементов
  const navConfig = [
    { id: "dashboard", title: "Панель управления", url: "/dashboard", icon: LayoutDashboard },
    { id: "comments", title: "Комментарии", url: "/comments", icon: MessageSquare, hasBadge: true, badgeVariant: "destructive" as const, badgeKey: "comments.new" },
    { id: "groups", title: "Группы", url: "/groups", icon: Users, hasBadge: true, badgeVariant: "secondary" as const, badgeKey: "groups.active" },
    { id: "keywords", title: "Ключевые слова", url: "/keywords", icon: Hash, hasBadge: true, badgeVariant: "outline" as const, badgeKey: "keywords.active" },
    { id: "monitoring", title: "Мониторинг", url: "/monitoring", icon: Monitor },
    { id: "parser", title: "Парсер", url: "/parser", icon: FileText },
    { id: "settings", title: "Настройки", url: "/settings", icon: Settings },
    { id: "profile", title: "Профиль", url: "/profile", icon: User },
  ];

  /**
   * Мемоизированный массив навигационных элементов sidebar.
   * Создает элементы навигации на основе конфигурации, добавляя badges с актуальными статистиками
   * и отмечая активный элемент на основе текущего пути.
   *
   * @returns {Array} Массив объектов навигационных элементов с id, title, url, icon, isActive и опционально badge
   */
  const navItems = useMemo(() => {
    const statsData: SidebarStats = stats || currentData.stats;

    return navConfig.map((item) => {
      const baseItem = {
        id: item.id,
        title: item.title,
        url: item.url,
        icon: item.icon,
        isActive: activePath === item.url,
      };

      // Добавляем badge если нужно
      if (item.hasBadge && item.badgeKey) {
        const badgeValue = item.badgeKey.split('.').reduce((obj, key) => obj?.[key], statsData as any);
        if (badgeValue) {
          return {
            ...baseItem,
            badge: (
              <Badge variant={item.badgeVariant} className="ml-auto">
                {badgeValue}
              </Badge>
            ),
          };
        }
      }

      return baseItem;
    });
  }, [stats, activePath, currentData.stats]);

  return {
    ...currentData,
    navItems,
    stats: stats || currentData.stats,
  };
};
