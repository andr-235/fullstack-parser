"use client";

import { useMemo } from "react";
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
import { SidebarData, SidebarStats } from "./types";

export const useSidebarData = (): SidebarData => {
  const { stats, activePath } = useNavigation();

  const user = useMemo(
    () => ({
      id: "1",
      name: "Администратор",
      email: "admin@vkparser.com",
      avatar: "/avatars/admin.svg",
      role: "admin" as const,
      status: "active" as const,
    }),
    []
  );

  const teams = useMemo(
    () => [
      {
        id: "1",
        name: "Парсер комментариев VK",
        logo: GalleryVerticalEnd,
        plan: "Корпоративная",
        status: "active" as const,
      },
    ],
    []
  );

  const projects = useMemo(
    () => [
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
    []
  );

  const navItems = useMemo(() => {
    const statsData: SidebarStats = stats || {
      comments: { new: 0, total: 0 },
      groups: { active: 0, total: 0 },
      keywords: { active: 0, total: 0 },
    };

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
  }, [stats, activePath]);

  return {
    user,
    teams,
    projects,
    navItems,
    stats: stats || {
      comments: { new: 0, total: 0 },
      groups: { active: 0, total: 0 },
      keywords: { active: 0, total: 0 },
    },
  };
};
