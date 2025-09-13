"use client";

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";

export default function RootPage() {
  // useRouteAccess автоматически перенаправит на нужную страницу
  useRouteAccess();
  
  return null;
}
