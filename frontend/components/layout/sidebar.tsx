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
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Дашборд', href: '/dashboard', icon: BarChart3 },
  { name: 'VK Группы', href: '/groups', icon: Users },
  { name: 'Ключевые слова', href: '/keywords', icon: KeyRound },
  { name: 'Комментарии', href: '/comments', icon: MessageSquare },
  { name: 'Парсер', href: '/parser', icon: Play },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 flex-shrink-0 bg-white dark:bg-gray-950 border-r border-gray-200 dark:border-gray-800 flex flex-col">
      <div className="flex items-center gap-2 p-4 h-16 border-b border-gray-200 dark:border-gray-800">
        <div className="text-2xl">📊</div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          VK Parser
        </h2>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                isActive
                  ? 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
              )}
            >
              <Icon className="mr-3 h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
        <div className="!mt-4 pt-4 border-t border-gray-200 dark:border-gray-800">
          <Link
            href="/settings"
            className={cn(
              'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
              pathname === '/settings'
                ? 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
            )}
          >
            <Settings className="mr-3 h-5 w-5" />
            Настройки
          </Link>
        </div>
      </nav>
    </aside>
  )
}
