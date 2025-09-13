"use client";

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";
import { UserProfile } from "@/features/auth";

// Отключаем статическую генерацию для приватных страниц
export const dynamic = 'force-dynamic'

export default function ProfilePage() {
  useRouteAccess(); // Проверяем доступ к приватной странице

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Профиль пользователя</h1>
        <p className="text-muted-foreground">
          Управление настройками аккаунта
        </p>
      </div>
      
      <UserProfile />
    </div>
  );
}
