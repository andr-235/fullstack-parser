"use client";

import * as React from "react";
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarRail,
} from "./custom/Sidebar";
import { GlassSidebar } from "@/shared/ui/glass-card/GlassSidebar";
import { NavMain } from "./NavMain";
import { useSidebarData } from "../model/useSidebarData";

export interface AppSidebarProps extends React.ComponentProps<typeof Sidebar> {}

export const AppSidebar: React.FC<AppSidebarProps> = ({ ...props }) => {
  const { navItems } = useSidebarData();

  return (
    <GlassSidebar className="min-h-screen w-64">
      <Sidebar 
        collapsible="icon" 
        className="border-r border-white/20 bg-transparent backdrop-blur-sm w-full flex flex-col"
        {...props}
      >
        <SidebarContent className="flex-1 gap-2 p-2">
          <NavMain items={navItems} />
        </SidebarContent>
        <SidebarRail />
      </Sidebar>
    </GlassSidebar>
  );
};
