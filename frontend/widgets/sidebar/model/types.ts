import { type LucideIcon } from "lucide-react";
import { type ReactNode } from "react";

export interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  role: "admin" | "user" | "moderator";
  status: "active" | "inactive" | "pending";
}

export interface Team {
  id: string;
  name: string;
  logo: LucideIcon;
  plan: string;
  status: "active" | "inactive";
}

export interface Project {
  id: string;
  name: string;
  url: string;
  icon: LucideIcon;
  status: "active" | "inactive" | "archived";
  description?: string;
}

export interface NavSubItem {
  id: string;
  title: string;
  url: string;
}

export interface NavItem {
  id: string;
  title: string;
  url: string;
  icon?: LucideIcon;
  isActive?: boolean;
  badge?: ReactNode;
  items?: NavSubItem[];
}

export interface SidebarStats {
  comments: {
    new: number;
    total: number;
  };
  groups: {
    active: number;
    total: number;
  };
  keywords: {
    active: number;
    total: number;
  };
}

export interface SidebarData {
  user: User;
  teams: Team[];
  projects: Project[];
  navItems: NavItem[];
  stats: SidebarStats;
}
