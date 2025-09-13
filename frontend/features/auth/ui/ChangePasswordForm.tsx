"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/ui/card";
import { Alert, AlertDescription } from "@/shared/ui/alert";
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
      <Card className="w-full max-w-md mx-auto">
        <CardContent className="pt-6">
          <div className="flex flex-col items-center space-y-4">
            <CheckCircle className="h-12 w-12 text-green-500" />
            <h3 className="text-lg font-semibold">Пароль успешно изменен</h3>
            <p className="text-sm text-muted-foreground text-center">
              Ваш пароль был успешно обновлен
            </p>
            <Button
              onClick={() => setSuccess(false)}
              variant="outline"
              className="w-full"
            >
              Изменить еще раз
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto bg-transparent border-white/20 backdrop-blur-sm">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl text-center text-white">Смена пароля</CardTitle>
        <CardDescription className="text-center text-white/70">
          Введите текущий пароль и новый пароль
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="current_password">Текущий пароль</Label>
            <div className="relative">
              <Input
                id="current_password"
                type={showCurrentPassword ? "text" : "password"}
                placeholder="Введите текущий пароль"
                {...register("current_password")}
                disabled={isLoading}
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                disabled={isLoading}
              >
                {showCurrentPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
            {errors.current_password && (
              <p className="text-sm text-red-500">{errors.current_password.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="new_password">Новый пароль</Label>
            <div className="relative">
              <Input
                id="new_password"
                type={showNewPassword ? "text" : "password"}
                placeholder="Введите новый пароль"
                {...register("new_password")}
                disabled={isLoading}
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                onClick={() => setShowNewPassword(!showNewPassword)}
                disabled={isLoading}
              >
                {showNewPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
            {errors.new_password && (
              <p className="text-sm text-red-500">{errors.new_password.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirm_password">Подтвердите пароль</Label>
            <div className="relative">
              <Input
                id="confirm_password"
                type={showConfirmPassword ? "text" : "password"}
                placeholder="Подтвердите новый пароль"
                {...register("confirm_password")}
                disabled={isLoading}
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                disabled={isLoading}
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
            {errors.confirm_password && (
              <p className="text-sm text-red-500">{errors.confirm_password.message}</p>
            )}
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Изменить пароль
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};
