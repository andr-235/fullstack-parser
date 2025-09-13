"use client";

import * as React from "react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/shared/ui/sidebar";
import { TeamSwitcher } from "./TeamSwitcher";
import { NavMain } from "./NavMain";
import { NavProjects } from "./NavProjects";
import { NavUser } from "./NavUser";
import { useSidebarData } from "../model/useSidebarData";

export interface AppSidebarProps extends React.ComponentProps<typeof Sidebar> {}

export const AppSidebar: React.FC<AppSidebarProps> = ({ ...props }) => {
  const { user, teams, projects, navItems } = useSidebarData();

  return (
    <Sidebar 
      collapsible="icon" 
      className="border-r border-border/50 bg-gradient-to-b from-background to-muted/20"
      {...props}
    >
      <SidebarHeader className="border-b border-border/30 bg-gradient-to-r from-primary/5 to-transparent">
        <TeamSwitcher teams={teams} />
      </SidebarHeader>
      <SidebarContent className="gap-2 p-2">
        <NavMain items={navItems} />
        <NavProjects projects={projects} />
      </SidebarContent>
      <SidebarFooter className="border-t border-border/30 bg-gradient-to-r from-muted/20 to-transparent">
        <NavUser user={user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
};
