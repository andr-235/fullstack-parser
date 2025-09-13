"use client";

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";

import { AuthWidget } from "@/widgets/auth";

export default function LoginPage() {
  useRouteAccess(); // Проверяем доступ к публичной странице

  return <AuthWidget />;
}
