"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Folder,
  Forward,
  MoreHorizontal,
  Trash2,
  type LucideIcon,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/shared/ui/dropdown-menu";
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/shared/ui/sidebar";
import { Project } from "../model/types";
import { useProjectActions } from "../model/useProjectActions";

export interface NavProjectsProps {
  projects: Project[];
}

export const NavProjects: React.FC<NavProjectsProps> = ({ projects }) => {
  const { isMobile } = useSidebar();
  const pathname = usePathname();
  const { handleViewProject, handleShareProject, handleDeleteProject } = useProjectActions();

  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden">
      <SidebarGroupLabel className="text-xs font-semibold text-muted-foreground uppercase tracking-wider px-2 py-1.5">
        Инструменты
      </SidebarGroupLabel>
      <SidebarMenu className="space-y-1">
        {projects.map((project) => (
          <SidebarMenuItem key={project.id} className="group">
            <SidebarMenuButton 
              asChild 
              isActive={pathname === project.url}
              className="hover:bg-accent/50 transition-all duration-200 rounded-lg group"
            >
              <Link href={project.url} className="flex items-center gap-3">
                <div className="flex size-4 items-center justify-center">
                  <project.icon className="size-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                </div>
                <span className="font-medium truncate">{project.name}</span>
              </Link>
            </SidebarMenuButton>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuAction showOnHover className="opacity-0 group-hover:opacity-100 transition-opacity">
                  <MoreHorizontal className="size-4" />
                  <span className="sr-only">Ещё</span>
                </SidebarMenuAction>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                className="w-48 rounded-xl border border-border/50 bg-background/95 backdrop-blur-sm shadow-xl"
                side={isMobile ? "bottom" : "right"}
                align={isMobile ? "end" : "start"}
              >
                <DropdownMenuItem 
                  onClick={() => handleViewProject(project.id)}
                  className="gap-3 p-2 rounded-lg hover:bg-accent/50 transition-colors cursor-pointer"
                >
                  <Folder className="size-4 text-muted-foreground" />
                  <span>Просмотреть проект</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator className="my-1" />
                <DropdownMenuItem 
                  onClick={() => handleShareProject(project.id)}
                  className="gap-3 p-2 rounded-lg hover:bg-accent/50 transition-colors cursor-pointer"
                >
                  <Forward className="size-4 text-muted-foreground" />
                  <span>Поделиться проектом</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator className="my-1" />
                <DropdownMenuItem 
                  onClick={() => handleDeleteProject(project.id)}
                  className="gap-3 p-2 rounded-lg hover:bg-destructive/10 hover:text-destructive transition-colors cursor-pointer"
                >
                  <Trash2 className="size-4 text-muted-foreground" />
                  <span>Удалить проект</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
    </SidebarGroup>
  );
};
