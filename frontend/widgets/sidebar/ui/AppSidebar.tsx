"use client";

import * as React from "react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "./custom/Sidebar";
import { GlassSidebar } from "@/shared/ui/glass-card/GlassSidebar";
import { NavMain } from "./NavMain";
import { NavUser } from "./NavUser";
import { useSidebarData } from "../model/useSidebarData";

export interface AppSidebarProps extends React.ComponentProps<typeof Sidebar> {}

export const AppSidebar: React.FC<AppSidebarProps> = ({ ...props }) => {
  const { user, navItems } = useSidebarData();

  return (
    <GlassSidebar className="min-h-screen w-64">
      <Sidebar 
        collapsible="icon" 
        className="border-r border-white/20 bg-transparent backdrop-blur-sm w-full"
        {...props}
      >
        <SidebarContent className="gap-2 p-2">
          <NavMain items={navItems} />
        </SidebarContent>
        <SidebarFooter className="border-t border-white/20 bg-transparent backdrop-blur-sm">
          <NavUser user={user} />
        </SidebarFooter>
        <SidebarRail />
      </Sidebar>
    </GlassSidebar>
  );
};
