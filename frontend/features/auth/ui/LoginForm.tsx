"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { GlassButton } from "@/shared/ui/glass-button";
import { GlassInput } from "@/shared/ui/glass-input";
import { Label } from "@/shared/ui/label";
import { GlassCard, GlassCardContent, GlassCardDescription, GlassCardHeader, GlassCardTitle } from "@/shared/ui/glass-card";
import { Alert, AlertDescription } from "@/shared/ui/alert";
import { GlassLayout } from "@/shared/ui/glass-layout";
import { Loader2, Eye, EyeOff } from "lucide-react";
import { useAuthStore } from "@/entities/user";
import { useDebounce } from "@/shared/hooks";
import type { LoginRequest } from "@/entities/user";

const loginSchema = z.object({
  email: z.string().email("Введите корректный email"),
  password: z.string().min(8, "Пароль должен содержать минимум 8 символов").regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, "Пароль должен содержать заглавные и строчные буквы, а также цифры"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginForm = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [attempts, setAttempts] = useState(0);
  const [lastAttempt, setLastAttempt] = useState(0);
  const [rateLimitError, setRateLimitError] = useState<string | null>(null);
  const { login, isLoading, error, clearError } = useAuthStore();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    const now = Date.now();
    const timeSinceLastAttempt = now - lastAttempt;

    // Rate limiting: max 5 attempts per minute
    if (attempts >= 5 && timeSinceLastAttempt < 60000) {
      setRateLimitError("Слишком много попыток. Попробуйте позже.");
      return;
    }

    clearError();
    setRateLimitError(null);
    setLastAttempt(now);
    setAttempts(prev => prev + 1);

    try {
      await login(data as LoginRequest);
      // Reset attempts on success
      setAttempts(0);
    } catch (error) {
      // Ошибка обрабатывается в store
    }
  };

  return (
    <GlassLayout>
      <GlassCard className="w-full max-w-md mx-auto">
        <GlassCardHeader className="space-y-3">
          <GlassCardTitle className="text-2xl text-center text-white">Вход в систему</GlassCardTitle>
          <GlassCardDescription className="text-center text-white/70">
            Введите email и пароль для входа
          </GlassCardDescription>
        </GlassCardHeader>
        <GlassCardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            {(error || rateLimitError) && (
              <Alert variant="destructive" className="border-red-400/30 bg-red-500/10">
                <AlertDescription className="text-red-200">{rateLimitError || error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-4">
              <Label htmlFor="email" className="text-white">Email</Label>
              <GlassInput
                id="email"
                type="email"
                placeholder="example@email.com"
                {...register("email")}
                disabled={isLoading}
              />
              {errors.email && (
                <p className="text-sm text-red-300">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-4">
              <Label htmlFor="password" className="text-white">Пароль</Label>
              <div className="relative">
                <GlassInput
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Введите пароль"
                  {...register("password")}
                  disabled={isLoading}
                  className="pr-10"
                />
                <GlassButton
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent text-white/70 hover:text-white"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </GlassButton>
              </div>
              {errors.password && (
                <p className="text-sm text-red-300">{errors.password.message}</p>
              )}
            </div>

            <GlassButton
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Войти
            </GlassButton>

            <div className="text-center">
              <Link
                href="/reset-password"
                className="inline-flex items-center text-sm text-blue-300 hover:text-blue-200 transition-colors hover:underline"
              >
                Забыли пароль?
              </Link>
            </div>
          </form>
        </GlassCardContent>
      </GlassCard>
    </GlassLayout>
  );
};
