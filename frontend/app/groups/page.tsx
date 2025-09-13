"use client";

// Отключаем статическую генерацию для приватных страниц
export const dynamic = 'force-dynamic'

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";

import { GroupsPage as GroupsPageComponent } from '@/features/groups'

export default function GroupsPage() {
  useRouteAccess(); // Проверяем доступ к приватной странице
  
  return <GroupsPageComponent />
}
