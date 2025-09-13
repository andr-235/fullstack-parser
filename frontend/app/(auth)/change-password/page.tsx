"use client";

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";

import { ChangePasswordPage as ChangePasswordPageWidget } from "@/widgets/auth";

export default function ChangePasswordPage() {
  useRouteAccess(); // Проверяем доступ к приватной странице

  return <ChangePasswordPageWidget />;
}
