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
import type { RegisterRequest } from "@/entities/user";

const registerSchema = z.object({
  full_name: z.string().min(2, "Имя должно содержать минимум 2 символа"),
  email: z.string().email("Введите корректный email"),
  password: z.string().min(8, "Пароль должен содержать минимум 8 символов"),
  confirm_password: z.string().min(8, "Подтвердите пароль"),
}).refine((data) => data.password === data.confirm_password, {
  message: "Пароли не совпадают",
  path: ["confirm_password"],
});

type RegisterFormData = z.infer<typeof registerSchema>;

export const RegisterForm = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [success, setSuccess] = useState(false);
  const { register: registerUser, isLoading, error, clearError } = useAuthStore();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    clearError();
    try {
      const requestData: RegisterRequest = {
        full_name: data.full_name,
        email: data.email,
        password: data.password,
      };

      await registerUser(requestData);
      setSuccess(true);
    } catch (error) {
      // Ошибка обрабатывается в store
    }
  };

  if (success) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardContent className="pt-6">
          <div className="flex flex-col items-center space-y-4">
            <CheckCircle className="h-12 w-12 text-green-500" />
            <h3 className="text-lg font-semibold">Регистрация успешна!</h3>
            <p className="text-sm text-muted-foreground text-center">
              Добро пожаловать! Вы успешно зарегистрированы и авторизованы.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto bg-transparent border-white/20 backdrop-blur-sm">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl text-center text-white">Регистрация</CardTitle>
        <CardDescription className="text-center text-white/70">
          Создайте новый аккаунт
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error.message}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="full_name" className="text-white">Полное имя</Label>
            <Input
              id="full_name"
              type="text"
              placeholder="Введите ваше имя"
              {...register("full_name")}
              disabled={isLoading}
              className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40 focus:ring-white/20"
            />
            {errors.full_name && (
              <p className="text-sm text-red-300">{errors.full_name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="email" className="text-white">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="example@email.com"
              {...register("email")}
              disabled={isLoading}
              className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40 focus:ring-white/20"
            />
            {errors.email && (
              <p className="text-sm text-red-300">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-white">Пароль</Label>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Введите пароль"
                {...register("password")}
                disabled={isLoading}
                className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40 focus:ring-white/20 pr-10"
              />
              <Button
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
              </Button>
            </div>
            {errors.password && (
              <p className="text-sm text-red-300">{errors.password.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirm_password" className="text-white">Подтвердите пароль</Label>
            <div className="relative">
              <Input
                id="confirm_password"
                type={showConfirmPassword ? "text" : "password"}
                placeholder="Подтвердите пароль"
                {...register("confirm_password")}
                disabled={isLoading}
                className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40 focus:ring-white/20 pr-10"
              />
              <Button
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
              </Button>
            </div>
            {errors.confirm_password && (
              <p className="text-sm text-red-300">{errors.confirm_password.message}</p>
            )}
          </div>

          <Button 
            type="submit" 
            className="w-full bg-white/20 hover:bg-white/30 text-white border border-white/20 backdrop-blur-sm transition-all duration-200" 
            disabled={isLoading}
          >
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Зарегистрироваться
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};
