"use client";

import { ReactNode } from "react";

interface GlassLayoutProps {
  children: ReactNode;
  className?: string;
}

export const GlassLayout = ({
  children,
  className = ""
}: GlassLayoutProps) => {
  return (
    <div className={`
      min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900
      ${className}
    `.trim()}>
      {children}
    </div>
  );
};