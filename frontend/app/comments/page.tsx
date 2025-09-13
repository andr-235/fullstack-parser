"use client";

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";
import { CommentsPage as CommentsPageComponent } from '@/features/comments'

export default function CommentsPage() {
  useRouteAccess(); // Проверяем доступ к приватной странице
  
  return <CommentsPageComponent />
}
