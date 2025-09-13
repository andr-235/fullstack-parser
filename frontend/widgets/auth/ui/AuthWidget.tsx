"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/ui/tabs";
import { GlassCard } from "@/shared/ui/glass-card";
import { LoginForm, RegisterForm, ChangePasswordForm, ResetPasswordForm } from "@/features/auth";

const TABS = [
  { value: "login", label: "Вход", component: LoginForm },
  { value: "register", label: "Регистрация", component: RegisterForm },
] as const;

export const AuthWidget = () => {
  const [activeTab, setActiveTab] = useState("login");

  return (
    <GlassCard>
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 bg-white/10 backdrop-blur-sm border border-white/20 gap-2 p-2">
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
    </GlassCard>
  );
};
