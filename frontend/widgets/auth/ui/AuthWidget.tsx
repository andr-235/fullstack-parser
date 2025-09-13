"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/ui/tabs";
import { LoginForm, ChangePasswordForm, ResetPasswordForm } from "@/features/auth";

export const AuthWidget = () => {
  const [activeTab, setActiveTab] = useState("login");

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="login">Вход</TabsTrigger>
            <TabsTrigger value="change-password">Смена пароля</TabsTrigger>
            <TabsTrigger value="reset-password">Сброс пароля</TabsTrigger>
          </TabsList>
          
          <TabsContent value="login" className="mt-6">
            <LoginForm />
          </TabsContent>
          
          <TabsContent value="change-password" className="mt-6">
            <ChangePasswordForm />
          </TabsContent>
          
          <TabsContent value="reset-password" className="mt-6">
            <ResetPasswordForm />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};
