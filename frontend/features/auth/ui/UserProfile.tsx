"use client";

import { useState } from "react";
import Link from "next/link";
import { GlassButton } from "@/shared/ui/glass-button";
import { GlassCard, GlassCardContent, GlassCardDescription, GlassCardHeader, GlassCardTitle } from "@/shared/ui/glass-card";
import { Badge } from "@/shared/ui/badge";
import { Separator } from "@/shared/ui/separator";
import { GlassLayout } from "@/shared/ui/glass-layout";
import { LogOut, User, Mail, Shield, Calendar, Key } from "lucide-react";
import { useAuthStore } from "@/entities/user";
import { format } from "date-fns";
import { ru } from "date-fns/locale";

export const UserProfile = () => {
  const { user, logout } = useAuthStore();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  if (!user) {
    return null;
  }

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      logout();
    } finally {
      setIsLoggingOut(false);
    }
  };

  return (
    <GlassLayout>
      <GlassCard className="w-full max-w-md mx-auto">
        <GlassCardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-white/10">
            <User className="h-10 w-10 text-white" />
          </div>
          <GlassCardTitle className="text-2xl">{user.full_name}</GlassCardTitle>
          <GlassCardDescription>{user.email}</GlassCardDescription>
        </GlassCardHeader>
        <GlassCardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <Mail className="h-4 w-4 text-white/70" />
              <span className="text-sm text-white/70">Email:</span>
              <span className="text-sm font-medium text-white">{user.email}</span>
            </div>

            <div className="flex items-center space-x-3">
              <Shield className="h-4 w-4 text-white/70" />
              <span className="text-sm text-white/70">Статус:</span>
              <Badge variant={user.is_active ? "default" : "secondary"} className="text-white">
                {user.is_active ? "Активен" : "Неактивен"}
              </Badge>
            </div>

            {user.is_superuser && (
              <div className="flex items-center space-x-3">
                <Shield className="h-4 w-4 text-white/70" />
                <span className="text-sm text-white/70">Роль:</span>
                <Badge variant="destructive" className="text-white">Администратор</Badge>
              </div>
            )}
          </div>

          <Separator className="bg-white/20" />

          <div className="space-y-3">
            <Link href="/change-password">
              <GlassButton
                variant="outline"
                className="w-full"
              >
                <Key className="mr-2 h-4 w-4" />
                Изменить пароль
              </GlassButton>
            </Link>

            <GlassButton
              onClick={handleLogout}
              variant="outline"
              className="w-full"
              disabled={isLoggingOut}
            >
              <LogOut className="mr-2 h-4 w-4" />
              {isLoggingOut ? "Выход..." : "Выйти из системы"}
            </GlassButton>
          </div>
        </GlassCardContent>
      </GlassCard>
    </GlassLayout>
  );
};
