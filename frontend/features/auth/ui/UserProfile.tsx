"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/shared/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/ui/card";
import { Badge } from "@/shared/ui/badge";
import { Separator } from "@/shared/ui/separator";
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
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="text-center">
        <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-primary/10">
          <User className="h-10 w-10 text-primary" />
        </div>
        <CardTitle className="text-2xl">{user.full_name}</CardTitle>
        <CardDescription>{user.email}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <Mail className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Email:</span>
            <span className="text-sm font-medium">{user.email}</span>
          </div>

          <div className="flex items-center space-x-3">
            <Shield className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Статус:</span>
            <Badge variant={user.is_active ? "default" : "secondary"}>
              {user.is_active ? "Активен" : "Неактивен"}
            </Badge>
          </div>

          {user.is_superuser && (
            <div className="flex items-center space-x-3">
              <Shield className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Роль:</span>
              <Badge variant="destructive">Администратор</Badge>
            </div>
          )}
        </div>

        <Separator />

        <div className="space-y-3">
          <Link href="/change-password">
            <Button
              variant="outline"
              className="w-full"
            >
              <Key className="mr-2 h-4 w-4" />
              Изменить пароль
            </Button>
          </Link>

          <Button
            onClick={handleLogout}
            variant="outline"
            className="w-full"
            disabled={isLoggingOut}
          >
            <LogOut className="mr-2 h-4 w-4" />
            {isLoggingOut ? "Выход..." : "Выйти из системы"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
