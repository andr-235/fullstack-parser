"use client";

// Отключаем статическую генерацию для приватных страниц
export const dynamic = 'force-dynamic'

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";
import { KeywordsPage as KeywordsPageComponent } from '@/features/keywords'

export default function KeywordsPage() {
  useRouteAccess(); // Проверяем доступ к приватной странице
  
  return <KeywordsPageComponent />
}
