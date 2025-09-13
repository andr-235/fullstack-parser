"use client";

import { ReactNode, useState } from "react";

interface CollapsibleProps {
  children: ReactNode;
  asChild?: boolean;
  defaultOpen?: boolean;
  className?: string;
}

export const Collapsible = ({ 
  children, 
  asChild = false, 
  defaultOpen = false, 
  className = "" 
}: CollapsibleProps) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const toggle = () => setIsOpen(!isOpen);

  if (asChild) {
    return (
      <div className={className} data-state={isOpen ? "open" : "closed"}>
        {children}
      </div>
    );
  }

  return (
    <div className={`${className}`} data-state={isOpen ? "open" : "closed"}>
      {children}
    </div>
  );
};

interface CollapsibleTriggerProps {
  children: ReactNode;
  asChild?: boolean;
  className?: string;
}

export const CollapsibleTrigger = ({ 
  children, 
  asChild = false, 
  className = "" 
}: CollapsibleTriggerProps) => {
  if (asChild) {
    return <div className={className}>{children}</div>;
  }

  return (
    <button className={className}>
      {children}
    </button>
  );
};

interface CollapsibleContentProps {
  children: ReactNode;
  className?: string;
}

export const CollapsibleContent = ({ children, className = "" }: CollapsibleContentProps) => {
  return (
    <div className={`overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down ${className}`}>
      {children}
    </div>
  );
};
