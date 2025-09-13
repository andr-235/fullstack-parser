"use client";

import * as React from "react";
import {
  BadgeCheck,
  Bell,
  ChevronsUpDown,
  CreditCard,
  LogOut,
  Sparkles,
} from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/shared/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/shared/ui/dropdown-menu";
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/shared/ui/sidebar";
import { User } from "../model/types";
import { useUserActions } from "../model/useUserActions";

export interface NavUserProps {
  user: User;
}

export const NavUser: React.FC<NavUserProps> = ({ user }) => {
  const { isMobile } = useSidebar();
  const { handleLogout, handleUpgrade, handleAccount, handleBilling, handleNotifications } = useUserActions();

  const userInitials = React.useMemo(
    () =>
      user.name
        .split(" ")
        .map((n) => n[0])
        .join(""),
    [user.name]
  );

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="group data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground hover:bg-sidebar-accent/50 transition-all duration-200"
            >
              <Avatar className="h-8 w-8 rounded-xl ring-2 ring-primary/20 group-hover:ring-primary/40 transition-all duration-200">
                <AvatarImage src={user.avatar} alt={user.name} />
                <AvatarFallback className="rounded-xl bg-gradient-to-br from-primary to-primary/80 text-primary-foreground font-semibold">
                  {userInitials}
                </AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold text-foreground">{user.name}</span>
                <span className="truncate text-xs text-muted-foreground">{user.email}</span>
              </div>
              <ChevronsUpDown className="ml-auto size-4 text-muted-foreground group-hover:text-foreground transition-colors" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-xl border border-border/50 bg-background/95 backdrop-blur-sm shadow-xl"
            side={isMobile ? "bottom" : "right"}
            align="end"
            sideOffset={4}
          >
            <DropdownMenuLabel className="p-0 font-normal">
              <div className="flex items-center gap-3 px-2 py-2 text-left text-sm">
                <Avatar className="h-8 w-8 rounded-xl ring-2 ring-primary/20">
                  <AvatarImage src={user.avatar} alt={user.name} />
                  <AvatarFallback className="rounded-xl bg-gradient-to-br from-primary to-primary/80 text-primary-foreground font-semibold">
                    {userInitials}
                  </AvatarFallback>
                </Avatar>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold text-foreground">{user.name}</span>
                  <span className="truncate text-xs text-muted-foreground">{user.email}</span>
                </div>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator className="my-1" />
            <DropdownMenuGroup>
              <DropdownMenuItem 
                onClick={handleUpgrade}
                className="gap-3 p-2 rounded-lg hover:bg-gradient-to-r hover:from-primary/10 hover:to-primary/5 transition-all cursor-pointer"
              >
                <Sparkles className="size-4 text-primary" />
                <span className="font-medium">Обновить до Pro</span>
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator className="my-1" />
            <DropdownMenuGroup>
              <DropdownMenuItem 
                onClick={handleAccount}
                className="gap-3 p-2 rounded-lg hover:bg-accent/50 transition-colors cursor-pointer"
              >
                <BadgeCheck className="size-4 text-muted-foreground" />
                <span>Аккаунт</span>
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={handleBilling}
                className="gap-3 p-2 rounded-lg hover:bg-accent/50 transition-colors cursor-pointer"
              >
                <CreditCard className="size-4 text-muted-foreground" />
                <span>Оплата</span>
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={handleNotifications}
                className="gap-3 p-2 rounded-lg hover:bg-accent/50 transition-colors cursor-pointer"
              >
                <Bell className="size-4 text-muted-foreground" />
                <span>Уведомления</span>
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator className="my-1" />
            <DropdownMenuItem 
              onClick={handleLogout}
              className="gap-3 p-2 rounded-lg hover:bg-destructive/10 hover:text-destructive transition-colors cursor-pointer"
            >
              <LogOut className="size-4 text-muted-foreground" />
              <span>Выйти</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
};
