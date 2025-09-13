"use client";

import { useEffect } from "react";


import { useRouter } from "next/navigation";

import { useAuth } from "@/features/auth/hooks";

import { AuthWidget } from "@/widgets/auth";

export default function LoginPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router]);

  return <AuthWidget />;
}
