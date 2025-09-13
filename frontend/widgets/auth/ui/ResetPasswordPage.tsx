"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/shared/ui/button";
import { GlassCard } from "@/shared/ui/glass-card";
import { ResetPasswordForm } from "@/features/auth";

export const ResetPasswordPage = () => {
  return (
    <GlassCard>
      <div className="mb-6">
        <Link href="/(auth)/login">
          <Button
            variant="ghost"
            size="sm"
            className="text-white/70 hover:text-white hover:bg-white/10 transition-colors"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Назад
          </Button>
        </Link>
      </div>
      <ResetPasswordForm />
    </GlassCard>
  );
};
