"use client";

import { ReactNode } from "react";
import { cn } from "@/shared/lib";

export interface GlassLayoutProps {
  children: ReactNode;
  variant?: "full" | "content" | "minimal";
  className?: string;
}

export const GlassLayout = ({
  children,
  variant = "content",
  className = ""
}: GlassLayoutProps) => {
  const baseClasses = "min-h-screen relative";

  const variantClasses = {
    full: "bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900",
    content: "bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900",
    minimal: "bg-slate-900"
  };

  const decorativeElements = variant === "full" || variant === "content" ? (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-600 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse" />
      <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-cyan-500 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse" />
      <div className="absolute top-40 left-1/2 w-60 h-60 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse" />
    </div>
  ) : null;

  const contentWrapper = variant === "full" ? (
    <div className="relative z-10 flex items-center justify-center min-h-screen p-4">
      <div className="w-full max-w-7xl">
        {children}
      </div>
    </div>
  ) : (
    <div className="relative z-10">
      {children}
    </div>
  );

  return (
    <div className={cn(baseClasses, variantClasses[variant], className)}>
      {decorativeElements}
      {contentWrapper}
    </div>
  );
};