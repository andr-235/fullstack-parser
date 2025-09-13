"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { toast } from "react-hot-toast";

export const useUserActions = () => {
  const router = useRouter();

  const handleLogout = useCallback(async () => {
    try {
      // TODO: Implement logout API call
      localStorage.removeItem("token");
      toast.success("Вы успешно вышли из системы");
      router.push("/login");
    } catch (error) {
      console.error("Logout error:", error);
      toast.error("Ошибка при выходе из системы");
    }
  }, [router]);

  const handleUpgrade = useCallback(() => {
    toast("Функция обновления будет доступна в ближайшее время");
    // TODO: Implement upgrade functionality
  }, []);

  const handleAccount = useCallback(() => {
    router.push("/account");
  }, [router]);

  const handleBilling = useCallback(() => {
    router.push("/billing");
  }, [router]);

  const handleNotifications = useCallback(() => {
    router.push("/notifications");
  }, [router]);

  return {
    handleLogout,
    handleUpgrade,
    handleAccount,
    handleBilling,
    handleNotifications,
  };
};
