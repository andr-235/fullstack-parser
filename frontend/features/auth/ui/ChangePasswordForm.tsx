"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { GlassButton } from "@/shared/ui/glass-button";
import { GlassInput } from "@/shared/ui/glass-input";
import { Label } from "@/shared/ui/label";
import { GlassCard, GlassCardContent, GlassCardDescription, GlassCardHeader, GlassCardTitle } from "@/shared/ui/glass-card";
import { Alert, AlertDescription } from "@/shared/ui/alert";
import { GlassLayout } from "@/shared/ui/glass-layout";
import { Loader2, Eye, EyeOff, CheckCircle } from "lucide-react";
import { useAuthStore } from "@/entities/user";
import { authApi } from "@/entities/user/api";
import type { ChangePasswordRequest } from "@/entities/user";

const changePasswordSchema = z.object({
  current_password: z.string().min(1, "Введите текущий пароль"),
  new_password: z.string().min(6, "Новый пароль должен содержать минимум 6 символов"),
  confirm_password: z.string().min(6, "Подтвердите пароль"),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Пароли не совпадают",
  path: ["confirm_password"],
});

type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

export const ChangePasswordForm = () => {
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const { clearError } = useAuthStore();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ChangePasswordFormData>({
    resolver: zodResolver(changePasswordSchema),
  });

  const onSubmit = async (data: ChangePasswordFormData) => {
    setError(null);
    setSuccess(false);
    setIsLoading(true);

    try {
      const requestData: ChangePasswordRequest = {
        current_password: data.current_password,
        new_password: data.new_password,
      };

      await authApi.changePassword(requestData);
      setSuccess(true);
      reset();
    } catch (error: any) {
      setError(error.message || "Ошибка при смене пароля");
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <GlassLayout>
        <GlassCard className="w-full max-w-md mx-auto">
          <GlassCardContent className="pt-6">
            <div className="flex flex-col items-center space-y-4">
              <CheckCircle className="h-12 w-12 text-green-400" />
              <h3 className="text-lg font-semibold text-white">Пароль успешно изменен</h3>
              <p className="text-sm text-white/70 text-center">
                Ваш пароль был успешно обновлен
              </p>
              <GlassButton
                onClick={() => setSuccess(false)}
                variant="outline"
                className="w-full"
              >
                Изменить еще раз
              </GlassButton>
            </div>
          </GlassCardContent>
        </GlassCard>
      </GlassLayout>
    );
  }

  return (
    <GlassLayout>
      <GlassCard className="w-full max-w-md mx-auto">
        <GlassCardHeader className="space-y-3">
          <GlassCardTitle className="text-2xl text-center text-white">Смена пароля</GlassCardTitle>
          <GlassCardDescription className="text-center text-white/70">
            Введите текущий пароль и новый пароль
          </GlassCardDescription>
        </GlassCardHeader>
        <GlassCardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            {error && (
              <Alert variant="destructive" className="border-red-400/30 bg-red-500/10">
                <AlertDescription className="text-red-200">{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-4">
              <Label htmlFor="current_password" className="text-white">Текущий пароль</Label>
              <div className="relative">
                <GlassInput
                  id="current_password"
                  type={showCurrentPassword ? "text" : "password"}
                  placeholder="Введите текущий пароль"
                  {...register("current_password")}
                  disabled={isLoading}
                  className="pr-10"
                />
                <GlassButton
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent text-white/70 hover:text-white"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  disabled={isLoading}
                >
                  {showCurrentPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </GlassButton>
              </div>
              {errors.current_password && (
                <p className="text-sm text-red-300">{errors.current_password.message}</p>
              )}
            </div>

            <div className="space-y-4">
              <Label htmlFor="new_password" className="text-white">Новый пароль</Label>
              <div className="relative">
                <GlassInput
                  id="new_password"
                  type={showNewPassword ? "text" : "password"}
                  placeholder="Введите новый пароль"
                  {...register("new_password")}
                  disabled={isLoading}
                  className="pr-10"
                />
                <GlassButton
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent text-white/70 hover:text-white"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  disabled={isLoading}
                >
                  {showNewPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </GlassButton>
              </div>
              {errors.new_password && (
                <p className="text-sm text-red-300">{errors.new_password.message}</p>
              )}
            </div>

            <div className="space-y-4">
              <Label htmlFor="confirm_password" className="text-white">Подтвердите пароль</Label>
              <div className="relative">
                <GlassInput
                  id="confirm_password"
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder="Подтвердите новый пароль"
                  {...register("confirm_password")}
                  disabled={isLoading}
                  className="pr-10"
                />
                <GlassButton
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent text-white/70 hover:text-white"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  disabled={isLoading}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </GlassButton>
              </div>
              {errors.confirm_password && (
                <p className="text-sm text-red-300">{errors.confirm_password.message}</p>
              )}
            </div>

            <GlassButton
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Изменить пароль
            </GlassButton>
          </form>
        </GlassCardContent>
      </GlassCard>
    </GlassLayout>
  );
};
