"use client";

// Отключаем статическую генерацию для приватных страниц
export const dynamic = 'force-dynamic'

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";

import { CommentsPage as CommentsPageComponent } from '@/features/comments'

export default function CommentsPage() {
  useRouteAccess(); // Проверяем доступ к приватной странице
  
  return <CommentsPageComponent />
}
