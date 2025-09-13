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
import { Loader2, CheckCircle, ArrowLeft } from "lucide-react";
import { authApi } from "@/entities/user/api";
import type { ResetPasswordRequest, ResetPasswordConfirmRequest } from "@/entities/user";

const resetPasswordSchema = z.object({
  email: z.string().email("Введите корректный email"),
});

const confirmResetSchema = z.object({
  token: z.string().min(1, "Введите код подтверждения"),
  new_password: z.string().min(6, "Пароль должен содержать минимум 6 символов"),
  confirm_password: z.string().min(6, "Подтвердите пароль"),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Пароли не совпадают",
  path: ["confirm_password"],
});

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;
type ConfirmResetFormData = z.infer<typeof confirmResetSchema>;

export const ResetPasswordForm = () => {
  const [step, setStep] = useState<"request" | "confirm">("request");
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register: registerRequest,
    handleSubmit: handleSubmitRequest,
    formState: { errors: requestErrors },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  });

  const {
    register: registerConfirm,
    handleSubmit: handleSubmitConfirm,
    formState: { errors: confirmErrors },
  } = useForm<ConfirmResetFormData>({
    resolver: zodResolver(confirmResetSchema),
  });

  const onRequestSubmit = async (data: ResetPasswordFormData) => {
    setError(null);
    setIsLoading(true);

    try {
      const requestData: ResetPasswordRequest = {
        email: data.email,
      };

      await authApi.resetPassword(requestData);
      setEmail(data.email);
      setStep("confirm");
      setSuccess(true);
    } catch (error: any) {
      setError(error.message || "Ошибка при запросе сброса пароля");
    } finally {
      setIsLoading(false);
    }
  };

  const onConfirmSubmit = async (data: ConfirmResetFormData) => {
    setError(null);
    setIsLoading(true);

    try {
      const requestData: ResetPasswordConfirmRequest = {
        token: data.token,
        new_password: data.new_password,
      };

      await authApi.resetPasswordConfirm(requestData);
      setSuccess(true);
    } catch (error: any) {
      setError(error.message || "Ошибка при подтверждении сброса пароля");
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    setStep("request");
    setError(null);
    setSuccess(false);
  };

  if (success && step === "confirm") {
    return (
      <Card className="w-full max-w-md mx-auto bg-transparent border-white/20 backdrop-blur-sm">
        <CardContent className="pt-6">
          <div className="flex flex-col items-center space-y-4">
            <CheckCircle className="h-12 w-12 text-blue-400" />
            <h3 className="text-lg font-semibold text-white">Пароль успешно сброшен</h3>
            <p className="text-sm text-white/70 text-center">
              Ваш пароль был успешно обновлен. Теперь вы можете войти в систему с новым паролем.
            </p>
            <Button
              onClick={() => {
                setStep("request");
                setSuccess(false);
              }}
              className="w-full bg-blue-600/20 hover:bg-blue-600/30 text-white border border-blue-500/30 backdrop-blur-sm transition-all duration-200"
            >
              Сбросить пароль еще раз
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (step === "request") {
    return (
      <Card className="w-full max-w-md mx-auto bg-transparent border-white/20 backdrop-blur-sm">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl text-center text-white">Сброс пароля</CardTitle>
          <CardDescription className="text-center text-white/70">
            Введите email для получения инструкций по сбросу пароля
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmitRequest(onRequestSubmit)} className="space-y-6">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-3">
              <Label htmlFor="email" className="text-white">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="example@email.com"
                {...registerRequest("email")}
                disabled={isLoading}
                className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40 focus:ring-white/20"
              />
              {requestErrors.email && (
                <p className="text-sm text-red-300">{requestErrors.email.message}</p>
              )}
            </div>

            <Button 
              type="submit" 
              className="w-full bg-blue-600/20 hover:bg-blue-600/30 text-white border border-blue-500/30 backdrop-blur-sm transition-all duration-200" 
              disabled={isLoading}
            >
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Отправить инструкции
            </Button>
          </form>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto bg-transparent border-white/20 backdrop-blur-sm">
      <CardHeader className="space-y-1">
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleBack}
            disabled={isLoading}
            className="text-white/70 hover:text-white hover:bg-white/10"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <CardTitle className="text-2xl text-white">Подтверждение сброса</CardTitle>
            <CardDescription className="text-white/70">
              Введите код подтверждения и новый пароль
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmitConfirm(onConfirmSubmit)} className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert className="bg-blue-500/20 border-blue-500/30">
              <CheckCircle className="h-4 w-4 text-blue-400" />
              <AlertDescription className="text-blue-200">
                Инструкции отправлены на {email}
              </AlertDescription>
            </Alert>
          )}

          <div className="space-y-3">
            <Label htmlFor="token" className="text-white">Код подтверждения</Label>
            <Input
              id="token"
              type="text"
              placeholder="Введите код из письма"
              {...registerConfirm("token")}
              disabled={isLoading}
              className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40 focus:ring-white/20"
            />
            {confirmErrors.token && (
              <p className="text-sm text-red-300">{confirmErrors.token.message}</p>
            )}
          </div>

          <div className="space-y-3">
            <Label htmlFor="new_password" className="text-white">Новый пароль</Label>
            <Input
              id="new_password"
              type="password"
              placeholder="Введите новый пароль"
              {...registerConfirm("new_password")}
              disabled={isLoading}
              className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40 focus:ring-white/20"
            />
            {confirmErrors.new_password && (
              <p className="text-sm text-red-300">{confirmErrors.new_password.message}</p>
            )}
          </div>

          <div className="space-y-3">
            <Label htmlFor="confirm_password" className="text-white">Подтвердите пароль</Label>
            <Input
              id="confirm_password"
              type="password"
              placeholder="Подтвердите новый пароль"
              {...registerConfirm("confirm_password")}
              disabled={isLoading}
              className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40 focus:ring-white/20"
            />
            {confirmErrors.confirm_password && (
              <p className="text-sm text-red-300">{confirmErrors.confirm_password.message}</p>
            )}
          </div>

          <Button 
            type="submit" 
            className="w-full bg-blue-600/20 hover:bg-blue-600/30 text-white border border-blue-500/30 backdrop-blur-sm transition-all duration-200" 
            disabled={isLoading}
          >
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Сбросить пароль
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};
