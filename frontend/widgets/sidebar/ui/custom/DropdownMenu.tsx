"use client";

import { ReactNode, useState, useRef, useEffect, createContext, useContext } from "react";

interface DropdownMenuContextType {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  triggerRef: React.RefObject<HTMLDivElement>;
}

const DropdownMenuContext = createContext<DropdownMenuContextType | null>(null);

interface DropdownMenuProps {
  children: ReactNode;
}

export const DropdownMenu = ({ children }: DropdownMenuProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const triggerRef = useRef<HTMLDivElement>(null);

  return (
    <DropdownMenuContext.Provider value={{ isOpen, setIsOpen, triggerRef }}>
      <div className="relative">{children}</div>
    </DropdownMenuContext.Provider>
  );
};

interface DropdownMenuTriggerProps {
  children: ReactNode;
  asChild?: boolean;
}

export const DropdownMenuTrigger = ({ children, asChild = false }: DropdownMenuTriggerProps) => {
  const context = useContext(DropdownMenuContext);
  if (!context) return null;

  const { setIsOpen, triggerRef } = context;

  const handleClick = () => {
    setIsOpen(!context.isOpen);
  };

  return (
    <div ref={triggerRef} className="cursor-pointer" onClick={handleClick}>
      {children}
    </div>
  );
};

interface DropdownMenuContentProps {
  children: ReactNode;
  className?: string;
  side?: "top" | "right" | "bottom" | "left";
  align?: "start" | "center" | "end";
  sideOffset?: number;
}

export const DropdownMenuContent = ({ 
  children, 
  className = "", 
  side = "bottom", 
  align = "start",
  sideOffset = 4
}: DropdownMenuContentProps) => {
  const context = useContext(DropdownMenuContext);
  if (!context) return null;

  const { isOpen, setIsOpen, triggerRef } = context;
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (contentRef.current && !contentRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
    
    return undefined;
  }, [isOpen, setIsOpen]);

  useEffect(() => {
    if (isOpen && triggerRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect();
      const contentRect = contentRef.current?.getBoundingClientRect();
      
      let top = 0;
      let left = 0;
      
      switch (side) {
        case "bottom":
          top = triggerRect.bottom + sideOffset;
          left = align === "start" ? triggerRect.left : 
                 align === "end" ? triggerRect.right - (contentRect?.width || 0) : 
                 triggerRect.left + (triggerRect.width - (contentRect?.width || 0)) / 2;
          break;
        case "top":
          top = triggerRect.top - (contentRect?.height || 0) - sideOffset;
          left = align === "start" ? triggerRect.left : 
                 align === "end" ? triggerRect.right - (contentRect?.width || 0) : 
                 triggerRect.left + (triggerRect.width - (contentRect?.width || 0)) / 2;
          break;
        case "right":
          top = align === "start" ? triggerRect.top : 
                align === "end" ? triggerRect.bottom - (contentRect?.height || 0) : 
                triggerRect.top + (triggerRect.height - (contentRect?.height || 0)) / 2;
          left = triggerRect.right + sideOffset;
          break;
        case "left":
          top = align === "start" ? triggerRect.top : 
                align === "end" ? triggerRect.bottom - (contentRect?.height || 0) : 
                triggerRect.top + (triggerRect.height - (contentRect?.height || 0)) / 2;
          left = triggerRect.left - (contentRect?.width || 0) - sideOffset;
          break;
      }
      
      setPosition({ top, left });
    }
  }, [isOpen, side, align, sideOffset, triggerRef]);

  if (!isOpen) return null;

  return (
    <div
      ref={contentRef}
      className={`fixed z-50 w-56 rounded-xl border border-white/20 bg-transparent backdrop-blur-sm shadow-xl ${className}`}
      style={{
        top: position.top,
        left: position.left,
      }}
    >
      {children}
    </div>
  );
};

interface DropdownMenuItemProps {
  children: ReactNode;
  onClick?: () => void;
  className?: string;
}

export const DropdownMenuItem = ({ children, onClick, className = "" }: DropdownMenuItemProps) => {
  return (
    <div 
      className={`gap-3 p-2 rounded-lg hover:bg-white/10 transition-colors cursor-pointer text-white ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

interface DropdownMenuLabelProps {
  children: ReactNode;
  className?: string;
}

export const DropdownMenuLabel = ({ children, className = "" }: DropdownMenuLabelProps) => {
  return (
    <div className={`p-0 font-normal ${className}`}>
      {children}
    </div>
  );
};

interface DropdownMenuGroupProps {
  children: ReactNode;
}

export const DropdownMenuGroup = ({ children }: DropdownMenuGroupProps) => {
  return <div className="space-y-1">{children}</div>;
};

interface DropdownMenuSeparatorProps {
  className?: string;
}

export const DropdownMenuSeparator = ({ className = "" }: DropdownMenuSeparatorProps) => {
  return <div className={`my-1 border-white/20 ${className}`} />;
};
