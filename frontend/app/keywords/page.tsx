"use client";

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";
import { KeywordsPage as KeywordsPageComponent } from '@/features/keywords'

export default function KeywordsPage() {
  useRouteAccess(); // Проверяем доступ к приватной странице
  
  return <KeywordsPageComponent />
}
