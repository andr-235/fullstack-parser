"use client";

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";

import { ResetPasswordPage as ResetPasswordPageWidget } from "@/widgets/auth";

export default function ResetPasswordPage() {
  useRouteAccess(); // Проверяем доступ к публичной странице

  return <ResetPasswordPageWidget />;
}
