"use client";

import { useRequireAuth } from "@/features/auth/hooks";
import { Loader2 } from "lucide-react";

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

export const ProtectedRoute = ({ 
  children, 
  redirectTo = "/login" 
}: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading } = useRequireAuth(redirectTo);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p className="text-sm text-muted-foreground">Загрузка...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // useRequireAuth перенаправит на страницу входа
  }

  return <>{children}</>;
};
