"use client";

import { ReactNode } from "react";

interface BadgeProps {
  children: ReactNode;
  variant?: "default" | "secondary" | "destructive" | "outline";
  className?: string;
}

export const Badge = ({ 
  children, 
  variant = "default", 
  className = "" 
}: BadgeProps) => {
  const variantClasses = {
    default: "bg-blue-600/20 text-blue-300 border border-blue-500/30",
    secondary: "bg-white/10 text-white/70 border border-white/20",
    destructive: "bg-red-600/20 text-red-300 border border-red-500/30",
    outline: "border border-white/20 text-white/70"
  };

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${variantClasses[variant]} ${className}`}>
      {children}
    </span>
  );
};
