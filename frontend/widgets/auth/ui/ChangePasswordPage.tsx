"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/shared/ui/button";
import { GlassCard } from "@/shared/ui/glass-card";
import { ChangePasswordForm } from "@/features/auth";

export const ChangePasswordPage = () => {
  return (
    <GlassCard>
      <div className="mb-6">
        <Link href="/profile">
          <Button
            variant="ghost"
            size="sm"
            className="text-white/70 hover:text-white hover:bg-white/10 transition-colors"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Назад к профилю
          </Button>
        </Link>
      </div>
      <ChangePasswordForm />
    </GlassCard>
  );
};
