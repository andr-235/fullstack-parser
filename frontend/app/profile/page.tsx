"use client";

  useRouteAccess(); // Проверяем доступ к приватной странице
import { useRouteAccess } from "@/shared/hooks/useRouteAccess";

import { UserProfile } from "@/features/auth";

export default function ProfilePage() {
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
