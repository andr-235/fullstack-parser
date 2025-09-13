'use client'

import * as React from 'react'

import {
  GalleryVerticalEnd,
  LayoutDashboard,
  MessageSquare,
  Users,
  Hash,
  Monitor,
  FileText,
  Settings,
} from 'lucide-react'

import { useNavigation } from '@/shared/contexts/NavigationContext'
import { Badge } from '@/shared/ui/badge'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from '@/shared/ui/sidebar'

import { NavMain } from './NavMain'
import { NavProjects } from './NavProjects'
import { NavUser } from './NavUser'
import { TeamSwitcher } from './TeamSwitcher'

// Sample data for user and teams
const user = {
  name: 'Администратор',
  email: 'admin@vkparser.com',
  avatar: '/avatars/admin.svg',
}

const teams = [
  {
    name: 'Парсер комментариев VK',
    logo: GalleryVerticalEnd,
    plan: 'Корпоративная',
  },
]

const projects = [
  {
    name: 'Мониторинг',
    url: '/monitoring',
    icon: Monitor,
  },
  {
    name: 'Парсер',
    url: '/parser',
    icon: FileText,
  },
  {
    name: 'Настройки',
    url: '/settings',
    icon: Settings,
  },
]

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { stats, activePath } = useNavigation()

  // Navigation items with dynamic badges
  const navMain = [
    {
      title: 'Панель управления',
      url: '/dashboard',
      icon: LayoutDashboard,
      isActive: activePath === '/dashboard',
    },
    {
      title: 'Комментарии',
      url: '/comments',
      icon: MessageSquare,
      isActive: activePath === '/comments',
      badge: stats?.comments.new ? (
        <Badge variant="destructive" className="ml-auto">
          {stats.comments.new}
        </Badge>
      ) : undefined,
    },
    {
      title: 'Группы',
      url: '/groups',
      icon: Users,
      isActive: activePath === '/groups',
      badge: stats?.groups.active ? (
        <Badge variant="secondary" className="ml-auto">
          {stats.groups.active}
        </Badge>
      ) : undefined,
    },
    {
      title: 'Ключевые слова',
      url: '/keywords',
      icon: Hash,
      isActive: activePath === '/keywords',
      badge: stats?.keywords.active ? (
        <Badge variant="outline" className="ml-auto">
          {stats.keywords.active}
        </Badge>
      ) : undefined,
    },
  ]

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <TeamSwitcher teams={teams} />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={navMain} />
        <NavProjects projects={projects} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
