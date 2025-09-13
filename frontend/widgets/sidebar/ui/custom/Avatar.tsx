"use client";

import { ReactNode } from "react";

interface AvatarProps {
  children: ReactNode;
  className?: string;
}

export const Avatar = ({ children, className = "" }: AvatarProps) => {
  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      {children}
    </div>
  );
};

interface AvatarImageProps {
  src?: string;
  alt?: string;
  className?: string;
}

export const AvatarImage = ({ src, alt, className = "" }: AvatarImageProps) => {
  if (!src) return null;
  
  return (
    <img 
      src={src} 
      alt={alt} 
      className={`w-full h-full object-cover ${className}`}
    />
  );
};

interface AvatarFallbackProps {
  children: ReactNode;
  className?: string;
}

export const AvatarFallback = ({ children, className = "" }: AvatarFallbackProps) => {
  return (
    <div className={`flex items-center justify-center w-full h-full bg-gradient-to-br from-blue-600/20 to-blue-600/10 text-white font-semibold border border-white/20 ${className}`}>
      {children}
    </div>
  );
};
