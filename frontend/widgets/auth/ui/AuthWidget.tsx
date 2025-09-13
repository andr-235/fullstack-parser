"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/ui/tabs";
import { LoginForm, RegisterForm, ChangePasswordForm, ResetPasswordForm } from "@/features/auth";

export const AuthWidget = () => {
  const [activeTab, setActiveTab] = useState("login");

  return (
    <div className="min-h-screen relative flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      {/* Красивый градиентный фон */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900" />
      
      {/* Размытые декоративные элементы */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse" />
        <div className="absolute top-40 left-1/2 w-60 h-60 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse" />
      </div>
      
      {/* Основной контент с размытием */}
      <div className="relative w-full max-w-md">
        <div className="backdrop-blur-xl bg-white/10 rounded-2xl shadow-2xl border border-white/20 p-8">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-4 bg-white/10 backdrop-blur-sm border border-white/20 gap-1 p-1">
              <TabsTrigger 
                value="login" 
                className="data-[state=active]:bg-white/20 data-[state=active]:text-white text-white/80 hover:text-white transition-colors rounded-md"
              >
                Вход
              </TabsTrigger>
              <TabsTrigger 
                value="register"
                className="data-[state=active]:bg-white/20 data-[state=active]:text-white text-white/80 hover:text-white transition-colors rounded-md"
              >
                Регистрация
              </TabsTrigger>
              <TabsTrigger 
                value="change-password"
                className="data-[state=active]:bg-white/20 data-[state=active]:text-white text-white/80 hover:text-white transition-colors rounded-md"
              >
                Смена пароля
              </TabsTrigger>
              <TabsTrigger 
                value="reset-password"
                className="data-[state=active]:bg-white/20 data-[state=active]:text-white text-white/80 hover:text-white transition-colors rounded-md"
              >
                Сброс пароля
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="login" className="mt-8">
              <LoginForm />
            </TabsContent>
            
            <TabsContent value="register" className="mt-8">
              <RegisterForm />
            </TabsContent>
            
            <TabsContent value="change-password" className="mt-8">
              <ChangePasswordForm />
            </TabsContent>
            
            <TabsContent value="reset-password" className="mt-8">
              <ResetPasswordForm />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};
