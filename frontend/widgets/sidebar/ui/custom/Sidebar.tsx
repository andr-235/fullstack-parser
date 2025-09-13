"use client";

import { ReactNode } from "react";

interface SidebarProps {
  children?: ReactNode;
  collapsible?: "icon" | "off";
  className?: string;
}

export const Sidebar = ({ children, collapsible = "off", className = "" }: SidebarProps) => {
  return (
    <aside className={`flex flex-col h-full ${className}`}>
      {children}
    </aside>
  );
};

export const SidebarContent = ({ children, className = "" }: { children: ReactNode; className?: string }) => {
  return (
    <div className={`flex-1 overflow-y-auto ${className}`}>
      {children}
    </div>
  );
};

export const SidebarFooter = ({ children, className = "" }: { children: ReactNode; className?: string }) => {
  return (
    <div className={`flex-shrink-0 ${className}`}>
      {children}
    </div>
  );
};

export const SidebarHeader = ({ children, className = "" }: { children: ReactNode; className?: string }) => {
  return (
    <div className={`flex-shrink-0 ${className}`}>
      {children}
    </div>
  );
};

export const SidebarRail = () => {
  return <div className="w-1 bg-white/20" />;
};
