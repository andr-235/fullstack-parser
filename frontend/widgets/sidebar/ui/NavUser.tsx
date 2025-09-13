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
import { Avatar, AvatarFallback, AvatarImage } from "./custom/Avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./custom/DropdownMenu";
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "./custom/SidebarMenu";
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
              className="group data-[state=open]:bg-white/10 data-[state=open]:text-white hover:bg-white/10 transition-all duration-200 text-white p-3"
            >
              <Avatar className="h-10 w-10 rounded-xl ring-2 ring-white/20 group-hover:ring-white/40 transition-all duration-200 flex-shrink-0">
                <AvatarImage src={user.avatar} alt={user.name} />
                <AvatarFallback className="rounded-xl bg-gradient-to-br from-blue-600/20 to-blue-600/10 text-white font-semibold border border-white/20">
                  {userInitials}
                </AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left text-sm leading-tight min-w-0">
                <span className="truncate font-semibold text-white">{user.name}</span>
                <span className="truncate text-xs text-white/70">{user.email}</span>
              </div>
              <ChevronsUpDown className="ml-auto size-4 text-white/70 group-hover:text-white transition-colors flex-shrink-0" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-xl border border-white/20 bg-transparent backdrop-blur-sm shadow-xl"
            side={isMobile ? "bottom" : "right"}
            align="end"
            sideOffset={4}
          >
            <DropdownMenuLabel className="p-0 font-normal">
              <div className="flex items-center gap-3 px-2 py-2 text-left text-sm">
                <Avatar className="h-8 w-8 rounded-xl ring-2 ring-white/20">
                  <AvatarImage src={user.avatar} alt={user.name} />
                  <AvatarFallback className="rounded-xl bg-gradient-to-br from-blue-600/20 to-blue-600/10 text-white font-semibold border border-white/20">
                    {userInitials}
                  </AvatarFallback>
                </Avatar>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold text-white">{user.name}</span>
                  <span className="truncate text-xs text-white/70">{user.email}</span>
                </div>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator className="my-1 border-white/20" />
            <DropdownMenuGroup>
              <DropdownMenuItem 
                onClick={handleUpgrade}
                className="gap-3 p-2 rounded-lg hover:bg-blue-600/20 transition-all cursor-pointer text-white"
              >
                <Sparkles className="size-4 text-blue-300" />
                <span className="font-medium">Обновить до Pro</span>
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator className="my-1 border-white/20" />
            <DropdownMenuGroup>
              <DropdownMenuItem 
                onClick={handleAccount}
                className="gap-3 p-2 rounded-lg hover:bg-white/10 transition-colors cursor-pointer text-white"
              >
                <BadgeCheck className="size-4 text-white/70" />
                <span>Аккаунт</span>
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={handleBilling}
                className="gap-3 p-2 rounded-lg hover:bg-white/10 transition-colors cursor-pointer text-white"
              >
                <CreditCard className="size-4 text-white/70" />
                <span>Оплата</span>
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={handleNotifications}
                className="gap-3 p-2 rounded-lg hover:bg-white/10 transition-colors cursor-pointer text-white"
              >
                <Bell className="size-4 text-white/70" />
                <span>Уведомления</span>
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator className="my-1 border-white/20" />
            <DropdownMenuItem 
              onClick={handleLogout}
              className="gap-3 p-2 rounded-lg hover:bg-red-600/20 hover:text-red-300 transition-colors cursor-pointer text-white"
            >
              <LogOut className="size-4 text-white/70" />
              <span>Выйти</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
};
