"use client";

import { ReactNode, memo } from "react";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  variant?: "default" | "gradient" | "primary" | "secondary" | "accent";
  hover?: boolean;
  padding?: "sm" | "md" | "lg";
}

export const GlassCard = memo(({
  children,
  className = "",
  variant = "default",
  hover = true,
  padding = "md"
}: GlassCardProps) => {
  const paddingClasses = {
    sm: "p-4",
    md: "p-6",
    lg: "p-8"
  };

  const variantClasses = {
    default: "bg-white/10 backdrop-blur-xl border border-white/20",
    gradient: "bg-gradient-to-r from-blue-500/25 via-purple-500/25 to-pink-500/25 backdrop-blur-xl border border-white/20",
    primary: "bg-gradient-to-r from-purple-600/25 via-blue-600/25 to-indigo-600/25 backdrop-blur-xl border border-white/20",
    secondary: "bg-gradient-to-r from-pink-500/25 via-red-500/25 to-orange-500/25 backdrop-blur-xl border border-white/20",
    accent: "bg-gradient-to-r from-green-500/25 via-teal-500/25 to-cyan-500/25 backdrop-blur-xl border border-white/20"
  };

  const baseClasses = `
    rounded-xl shadow-2xl
    ${variantClasses[variant]}
    ${hover ? 'glass-hover' : ''}
    ${paddingClasses[padding]}
    ${className}
  `.trim();

  return (
    <div className={baseClasses}>
      {children}
    </div>
  );
});
GlassCard.displayName = "GlassCard";

interface GlassCardHeaderProps {
  children: ReactNode;
  className?: string;
}

export const GlassCardHeader = ({
  children,
  className = ""
}: GlassCardHeaderProps) => {
  return (
    <div className={`pb-4 ${className}`}>
      {children}
    </div>
  );
};

interface GlassCardTitleProps {
  children: ReactNode;
  className?: string;
  id?: string;
}

export const GlassCardTitle = ({
  children,
  className = "",
  id
}: GlassCardTitleProps) => {
  return (
    <h3 id={id} className={`text-xl font-semibold text-white ${className}`}>
      {children}
    </h3>
  );
};

interface GlassCardDescriptionProps {
  children: ReactNode;
  className?: string;
}

export const GlassCardDescription = ({
  children,
  className = ""
}: GlassCardDescriptionProps) => {
  return (
    <p className={`text-sm text-white/70 ${className}`}>
      {children}
    </p>
  );
};

interface GlassCardContentProps {
  children: ReactNode;
  className?: string;
}

export const GlassCardContent = ({
  children,
  className = ""
}: GlassCardContentProps) => {
  return (
    <div className={className}>
      {children}
    </div>
  );
};