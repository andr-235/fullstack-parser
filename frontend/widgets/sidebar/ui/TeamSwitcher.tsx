"use client";

import * as React from "react";
import { ChevronsUpDown, Plus } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuTrigger,
} from "@/shared/ui/dropdown-menu";
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/shared/ui/sidebar";
import { Team } from "../model/types";

export interface TeamSwitcherProps {
  teams: Team[];
}

export const TeamSwitcher: React.FC<TeamSwitcherProps> = ({ teams }) => {
  const { isMobile } = useSidebar();
  const [activeTeam, setActiveTeam] = React.useState<Team>(teams[0]!);

  const handleTeamSelect = React.useCallback((team: Team) => {
    setActiveTeam(team);
  }, []);

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="group data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground hover:bg-sidebar-accent/50 transition-all duration-200"
            >
              <div className="flex aspect-square size-8 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary/80 text-primary-foreground shadow-sm ring-1 ring-primary/20 group-hover:shadow-md group-hover:scale-105 transition-all duration-200">
                <activeTeam.logo className="size-4" />
              </div>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold text-foreground">{activeTeam.name}</span>
                <span className="truncate text-xs text-muted-foreground">{activeTeam.plan}</span>
              </div>
              <ChevronsUpDown className="ml-auto size-4 text-muted-foreground group-hover:text-foreground transition-colors" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-xl border border-border/50 bg-background/95 backdrop-blur-sm shadow-xl"
            align="start"
            side={isMobile ? "bottom" : "right"}
            sideOffset={4}
          >
            <DropdownMenuLabel className="text-xs text-muted-foreground px-2 py-1.5 font-medium">
              Команды
            </DropdownMenuLabel>
            {teams.map((team, index) => (
              <DropdownMenuItem
                key={team.id}
                onClick={() => handleTeamSelect(team)}
                className="gap-3 p-2 rounded-lg hover:bg-accent/50 transition-colors cursor-pointer"
              >
                <div className="flex size-6 items-center justify-center rounded-lg bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/20">
                  <team.logo className="size-4 shrink-0 text-primary" />
                </div>
                <span className="font-medium">{team.name}</span>
                <DropdownMenuShortcut className="text-xs">⌘{index + 1}</DropdownMenuShortcut>
              </DropdownMenuItem>
            ))}
            <DropdownMenuSeparator className="my-1" />
            <DropdownMenuItem className="gap-3 p-2 rounded-lg hover:bg-accent/50 transition-colors cursor-pointer">
              <div className="flex size-6 items-center justify-center rounded-lg border border-dashed border-muted-foreground/30 bg-muted/30">
                <Plus className="size-4 text-muted-foreground" />
              </div>
              <div className="font-medium text-muted-foreground">
                Добавить команду
              </div>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
};
