"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/ui/tabs";
import { LoginForm, RegisterForm, ChangePasswordForm, ResetPasswordForm } from "@/features/auth";

const TABS = [
  { value: "login", label: "Вход", component: LoginForm },
  { value: "register", label: "Регистрация", component: RegisterForm },
  { value: "change-password", label: "Смена пароля", component: ChangePasswordForm },
  { value: "reset-password", label: "Сброс пароля", component: ResetPasswordForm },
] as const;

export const AuthWidget = () => {
  const [activeTab, setActiveTab] = useState("login");

  return (
    <div className="min-h-screen relative flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      {/* Красивый градиентный фон */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900" />
      
      {/* Размытые декоративные элементы */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-600 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-cyan-500 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse" />
        <div className="absolute top-40 left-1/2 w-60 h-60 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse" />
      </div>
      
      {/* Основной контент с размытием */}
      <div className="relative w-full max-w-md">
        <div className="backdrop-blur-xl bg-white/10 rounded-2xl shadow-2xl border border-white/20 p-8">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="flex w-full bg-white/10 backdrop-blur-sm border border-white/20 gap-2 p-2 justify-between">
              {TABS.map((tab) => (
                <TabsTrigger 
                  key={tab.value}
                  value={tab.value} 
                  className="data-[state=active]:bg-white/20 data-[state=active]:text-white text-white/80 hover:text-white transition-colors rounded-md px-2 py-1 text-xs"
                >
                  {tab.label}
                </TabsTrigger>
              ))}
            </TabsList>
            
            {TABS.map((tab) => {
              const Component = tab.component;
              return (
                <TabsContent key={tab.value} value={tab.value} className="mt-10">
                  <Component />
                </TabsContent>
              );
            })}
          </Tabs>
        </div>
      </div>
    </div>
  );
};
