"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, type LucideIcon } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/shared/ui/collapsible";
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/shared/ui/sidebar";
import { NavItem } from "../model/types";

export interface NavMainProps {
  items: NavItem[];
}

export const NavMain: React.FC<NavMainProps> = ({ items }) => {
  const pathname = usePathname();

  return (
    <SidebarGroup>
      <SidebarGroupLabel className="text-xs font-semibold text-muted-foreground uppercase tracking-wider px-2 py-1.5">
        Платформа
      </SidebarGroupLabel>
      <SidebarMenu className="space-y-1">
        {items.map((item) => (
          <Collapsible
            key={item.id}
            asChild
            defaultOpen={item.isActive ?? false}
            className="group/collapsible"
          >
            <SidebarMenuItem>
              <CollapsibleTrigger asChild>
                <SidebarMenuButton
                  asChild
                  tooltip={item.title}
                  isActive={pathname === item.url}
                  className="group hover:bg-accent/50 transition-all duration-200 rounded-lg"
                >
                  <Link href={item.url} className="flex items-center gap-3">
                    {item.icon && (
                      <item.icon className="size-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                    )}
                    <span className="font-medium">{item.title}</span>
                    {item.badge}
                    <ChevronRight className="ml-auto size-4 text-muted-foreground group-data-[state=open]:rotate-90 transition-transform" />
                  </Link>
                </SidebarMenuButton>
              </CollapsibleTrigger>
              {item.items?.length ? (
                <CollapsibleContent className="overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down">
                  <SidebarMenuSub className="ml-4 mt-1 space-y-1">
                    {item.items?.map((subItem) => (
                      <SidebarMenuSubItem key={subItem.id}>
                        <SidebarMenuSubButton
                          asChild
                          isActive={pathname === subItem.url}
                          className="hover:bg-accent/30 transition-colors rounded-md"
                        >
                          <Link href={subItem.url} className="text-sm">
                            <span>{subItem.title}</span>
                          </Link>
                        </SidebarMenuSubButton>
                      </SidebarMenuSubItem>
                    ))}
                  </SidebarMenuSub>
                </CollapsibleContent>
              ) : null}
            </SidebarMenuItem>
          </Collapsible>
        ))}
      </SidebarMenu>
    </SidebarGroup>
  );
};
