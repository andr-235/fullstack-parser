"use client";

// Отключаем статическую генерацию для приватных страниц
export const dynamic = 'force-dynamic'

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";

import { DashboardWidget } from "@/widgets/dashboard";

export default function DashboardPage() {
  useRouteAccess(); // Проверяем доступ к приватной странице

  return <DashboardWidget />;
}
