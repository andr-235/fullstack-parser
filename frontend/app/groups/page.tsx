"use client";

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";
import { GroupsPage as GroupsPageComponent } from '@/features/groups'

export default function GroupsPage() {
  useRouteAccess(); // Проверяем доступ к приватной странице
  
  return <GroupsPageComponent />
}
