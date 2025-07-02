'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  BarChart3, 
  Users, 
  KeyRound, 
  MessageSquare, 
  Play,
  Settings,
  Menu,
  X
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useState } from 'react'

interface SidebarProps {
  className?: string
}

const navigationItems = [
  {
    title: 'Дашборд',
    href: '/dashboard',
    icon: BarChart3,
  },
  {
    title: 'VK Группы',
    href: '/groups',
    icon: Users,
  },
  {
    title: 'Ключевые слова',
    href: '/keywords',
    icon: KeyRound,
  },
  {
    title: 'Комментарии',
    href: '/comments',
    icon: MessageSquare,
  },
  {
    title: 'Парсер',
    href: '/parser',
    icon: Play,
  },
  {
    title: 'Настройки',
    href: '/settings',
    icon: Settings,
  },
]

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname()
  const [isCollapsed, setIsCollapsed] = useState(false)

  return (
    <div className={cn(
      "flex flex-col bg-white border-r border-gray-200 transition-all duration-300",
      isCollapsed ? "w-16" : "w-64",
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <div className="text-2xl">📊</div>
            <h2 className="text-lg font-semibold text-gray-900">
              VK Parser
            </h2>
          </div>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1 rounded-lg hover:bg-gray-100"
        >
          {isCollapsed ? <Menu size={20} /> : <X size={20} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigationItems.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-blue-100 text-blue-700"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              )}
              title={isCollapsed ? item.title : undefined}
            >
              <Icon size={20} />
              {!isCollapsed && <span>{item.title}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className={cn(
          "flex items-center gap-3 px-3 py-2 text-sm text-gray-500",
          isCollapsed && "justify-center"
        )}>
          {!isCollapsed ? (
            <span>v1.0.0</span>
          ) : (
            <span className="text-xs">v1</span>
          )}
        </div>
      </div>
    </div>
  )
} 