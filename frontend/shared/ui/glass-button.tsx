"use client";

import { ReactNode, memo } from "react";

interface GlassButtonProps {
  children: ReactNode;
  className?: string;
  variant?: "default" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
  type?: "button" | "submit" | "reset";
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
}

export const GlassButton = memo(({
  children,
  className = "",
  variant = "default",
  size = "md",
  type = "button",
  onClick,
  disabled = false,
  loading = false
}: GlassButtonProps) => {
  const sizeClasses = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg"
  };

  const variantClasses = {
    default: "bg-white/15 backdrop-blur-sm border border-white/25 text-white hover:bg-white/25",
    outline: "bg-transparent border border-white/35 text-white hover:bg-white/15",
    ghost: "bg-transparent text-white hover:bg-white/15"
  };

  const baseClasses = `
    rounded-md font-medium transition-all duration-200
    ${variantClasses[variant]}
    ${sizeClasses[size]}
    ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
    ${className}
  `.trim();

  return (
    <button
      className={baseClasses}
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading ? (
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          <span>Загрузка...</span>
        </div>
      ) : (
        children
      )}
    </button>
  );
});
GlassButton.displayName = "GlassButton";