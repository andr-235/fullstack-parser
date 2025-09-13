"use client";

export const dynamic = 'force-dynamic'

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";

import { GroupsPage as GroupsPageComponent } from '@/features/groups'

export default function GroupsPage() {
  useRouteAccess();
  return <GroupsPageComponent />
}
