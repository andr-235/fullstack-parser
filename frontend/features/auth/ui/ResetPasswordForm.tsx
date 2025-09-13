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
      <GlassLayout>
        <GlassCard className="w-full max-w-md mx-auto">
          <GlassCardContent className="pt-6">
            <div className="flex flex-col items-center space-y-4">
              <CheckCircle className="h-12 w-12 text-blue-400" />
              <h3 className="text-lg font-semibold text-white">Пароль успешно сброшен</h3>
              <p className="text-sm text-white/70 text-center">
                Ваш пароль был успешно обновлен. Теперь вы можете войти в систему с новым паролем.
              </p>
              <GlassButton
                onClick={() => {
                  setStep("request");
                  setSuccess(false);
                }}
                className="w-full"
              >
                Сбросить пароль еще раз
              </GlassButton>
            </div>
          </GlassCardContent>
        </GlassCard>
      </GlassLayout>
    );
  }

  if (step === "request") {
    return (
      <GlassLayout>
        <GlassCard className="w-full max-w-md mx-auto">
          <GlassCardHeader className="space-y-3">
            <GlassCardTitle className="text-2xl text-center text-white">Сброс пароля</GlassCardTitle>
            <GlassCardDescription className="text-center text-white/70">
              Введите email для получения инструкций по сбросу пароля
            </GlassCardDescription>
          </GlassCardHeader>
          <GlassCardContent>
            <form onSubmit={handleSubmitRequest(onRequestSubmit)} className="space-y-8">
              {error && (
                <Alert variant="destructive" className="border-red-400/30 bg-red-500/10">
                  <AlertDescription className="text-red-200">{error}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-4">
                <Label htmlFor="email" className="text-white">Email</Label>
                <GlassInput
                  id="email"
                  type="email"
                  placeholder="example@email.com"
                  {...registerRequest("email")}
                  disabled={isLoading}
                />
                {requestErrors.email && (
                  <p className="text-sm text-red-300">{requestErrors.email.message}</p>
                )}
              </div>

              <GlassButton
                type="submit"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Отправить инструкции
              </GlassButton>
            </form>
          </GlassCardContent>
        </GlassCard>
      </GlassLayout>
    );
  }

  return (
    <GlassLayout>
      <GlassCard className="w-full max-w-md mx-auto">
        <GlassCardHeader className="space-y-1">
          <div className="flex items-center space-x-2">
            <GlassButton
              variant="ghost"
              size="sm"
              onClick={handleBack}
              disabled={isLoading}
              className="text-white/70 hover:text-white hover:bg-white/10"
            >
              <ArrowLeft className="h-4 w-4" />
            </GlassButton>
            <div>
              <GlassCardTitle className="text-2xl text-white">Подтверждение сброса</GlassCardTitle>
              <GlassCardDescription className="text-white/70">
                Введите код подтверждения и новый пароль
              </GlassCardDescription>
            </div>
          </div>
        </GlassCardHeader>
        <GlassCardContent>
          <form onSubmit={handleSubmitConfirm(onConfirmSubmit)} className="space-y-8">
            {error && (
              <Alert variant="destructive" className="border-red-400/30 bg-red-500/10">
                <AlertDescription className="text-red-200">{error}</AlertDescription>
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

            <div className="space-y-4">
              <Label htmlFor="token" className="text-white">Код подтверждения</Label>
              <GlassInput
                id="token"
                type="text"
                placeholder="Введите код из письма"
                {...registerConfirm("token")}
                disabled={isLoading}
              />
              {confirmErrors.token && (
                <p className="text-sm text-red-300">{confirmErrors.token.message}</p>
              )}
            </div>

            <div className="space-y-4">
              <Label htmlFor="new_password" className="text-white">Новый пароль</Label>
              <GlassInput
                id="new_password"
                type="password"
                placeholder="Введите новый пароль"
                {...registerConfirm("new_password")}
                disabled={isLoading}
              />
              {confirmErrors.new_password && (
                <p className="text-sm text-red-300">{confirmErrors.new_password.message}</p>
              )}
            </div>

            <div className="space-y-4">
              <Label htmlFor="confirm_password" className="text-white">Подтвердите пароль</Label>
              <GlassInput
                id="confirm_password"
                type="password"
                placeholder="Подтвердите новый пароль"
                {...registerConfirm("confirm_password")}
                disabled={isLoading}
              />
              {confirmErrors.confirm_password && (
                <p className="text-sm text-red-300">{confirmErrors.confirm_password.message}</p>
              )}
            </div>

            <GlassButton
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Сбросить пароль
            </GlassButton>
          </form>
        </GlassCardContent>
      </GlassCard>
    </GlassLayout>
  );
};
