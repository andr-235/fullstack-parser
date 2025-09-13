"use client";

import { ReactNode } from "react";

interface SidebarMenuProps {
  children: ReactNode;
  className?: string;
}

export const SidebarMenu = ({ children, className = "" }: SidebarMenuProps) => {
  return (
    <ul className={`space-y-1 ${className}`}>
      {children}
    </ul>
  );
};

export const SidebarMenuItem = ({ children, className = "" }: { children: ReactNode; className?: string }) => {
  return (
    <li className={className}>
      {children}
    </li>
  );
};

interface SidebarMenuButtonProps {
  children: ReactNode;
  asChild?: boolean;
  isActive?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
  tooltip?: string;
}

export const SidebarMenuButton = ({ 
  children, 
  asChild = false, 
  isActive = false, 
  size = "md",
  className = "",
  tooltip
}: SidebarMenuButtonProps) => {
  const sizeClasses = {
    sm: "h-8 px-3 text-sm",
    md: "h-10 px-4 text-sm",
    lg: "h-14 px-5 text-base"
  };

  const baseClasses = "flex items-center gap-3 w-full rounded-lg transition-all duration-200 cursor-pointer";
  const activeClasses = isActive ? "bg-white/20 text-white" : "text-white/70 hover:text-white hover:bg-white/10";
  
  if (asChild) {
    return (
      <div className={`${baseClasses} ${activeClasses} ${sizeClasses[size]} ${className}`} title={tooltip}>
        {children}
      </div>
    );
  }

  return (
    <button 
      className={`${baseClasses} ${activeClasses} ${sizeClasses[size]} ${className}`}
      title={tooltip}
    >
      {children}
    </button>
  );
};

export const SidebarMenuAction = ({ 
  children, 
  showOnHover = false, 
  className = "" 
}: { 
  children: ReactNode; 
  showOnHover?: boolean; 
  className?: string;
}) => {
  return (
    <div className={`${showOnHover ? "opacity-0 group-hover:opacity-100" : ""} transition-opacity ${className}`}>
      {children}
    </div>
  );
};

export const SidebarMenuSub = ({ children, className = "" }: { children: ReactNode; className?: string }) => {
  return (
    <ul className={`space-y-1 ${className}`}>
      {children}
    </ul>
  );
};

export const SidebarMenuSubItem = ({ children, className = "" }: { children: ReactNode; className?: string }) => {
  return (
    <li className={className}>
      {children}
    </li>
  );
};

export const SidebarMenuSubButton = ({ 
  children, 
  asChild = false, 
  isActive = false, 
  className = "" 
}: { 
  children: ReactNode; 
  asChild?: boolean; 
  isActive?: boolean; 
  className?: string;
}) => {
  const baseClasses = "flex items-center gap-3 w-full rounded-md transition-all duration-200 cursor-pointer px-3 py-2";
  const activeClasses = isActive ? "bg-white/20 text-white" : "text-white/70 hover:text-white hover:bg-white/10";
  
  if (asChild) {
    return (
      <div className={`${baseClasses} ${activeClasses} ${className}`}>
        {children}
      </div>
    );
  }

  return (
    <button className={`${baseClasses} ${activeClasses} ${className}`}>
      {children}
    </button>
  );
};

export const SidebarGroup = ({ children, className = "" }: { children: ReactNode; className?: string }) => {
  return (
    <div className={`space-y-2 ${className}`}>
      {children}
    </div>
  );
};

export const SidebarGroupLabel = ({ children, className = "" }: { children: ReactNode; className?: string }) => {
  return (
    <div className={`text-xs font-semibold text-white/70 uppercase tracking-wider px-2 py-1.5 ${className}`}>
      {children}
    </div>
  );
};

export const useSidebar = () => {
  return {
    isMobile: false,
    isOpen: true,
    toggle: () => {},
    open: () => {},
    close: () => {}
  };
};
