"use client";

import { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  padding?: "sm" | "md" | "lg";
}

export const Card = ({
  children,
  className = "",
  hover = true,
  padding = "md"
}: CardProps) => {
  const paddingClasses = {
    sm: "p-4",
    md: "p-6",
    lg: "p-8"
  };

  const baseClasses = `
    backdrop-blur-xl bg-white/10 rounded-xl shadow-2xl border border-white/20
    ${hover ? 'hover:bg-white/15 transition-colors duration-200' : ''}
    ${paddingClasses[padding]}
    ${className}
  `.trim();

  return (
    <div className={baseClasses}>
      {children}
    </div>
  );
};

// Обратная совместимость
export const CustomCard = Card;
