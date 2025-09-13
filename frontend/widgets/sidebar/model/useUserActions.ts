"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { toast } from "react-hot-toast";
import { useAuthStore } from "@/entities/user";
import { useSidebarStore } from "./sidebar-store";

/**
 * Хук для действий пользователя в sidebar
 */
export const useUserActions = () => {
  const router = useRouter();
  const { logout } = useAuthStore();
  const { updateUserProfile, isLoading, error } = useSidebarStore();

  const handleLogout = useCallback(async () => {
    try {
      await logout();
      toast.success("Вы успешно вышли из системы");
      router.push("/login");
    } catch (error: any) {
      console.error("Logout error:", error);
      toast.error(error.message || "Ошибка при выходе из системы");
    }
  }, [logout, router]);

  const handleUpgrade = useCallback(() => {
    toast("Функция обновления будет доступна в ближайшее время");
    // TODO: Implement upgrade functionality
  }, []);

  const handleAccount = useCallback(() => {
    router.push("/profile");
  }, [router]);

  const handleBilling = useCallback(() => {
    router.push("/billing");
  }, [router]);

  const handleNotifications = useCallback(() => {
    router.push("/notifications");
  }, [router]);

  const handleUpdateProfile = useCallback(async (data: {
    name?: string;
    email?: string;
    avatar?: string;
  }) => {
    try {
      await updateUserProfile(data);
      toast.success("Профиль успешно обновлен");
    } catch (error: any) {
      console.error("Update profile error:", error);
      toast.error(error.message || "Ошибка обновления профиля");
    }
  }, [updateUserProfile]);

  return {
    handleLogout,
    handleUpgrade,
    handleAccount,
    handleBilling,
    handleNotifications,
    handleUpdateProfile,
    isLoading,
    error,
  };
};
