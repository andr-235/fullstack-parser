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
  Activity,
} from 'lucide-react'
import { cn } from '@/shared/lib/utils'
import { AppIcon } from '@/shared/ui'

const navigation = [
  { name: 'Дашборд', href: '/dashboard', icon: BarChart3 },
  { name: 'VK Группы', href: '/groups', icon: Users },
  { name: 'Ключевые слова', href: '/keywords', icon: KeyRound },
  { name: 'Комментарии', href: '/comments', icon: MessageSquare },
  { name: 'Парсер', href: '/parser', icon: Play },
  { name: 'Мониторинг', href: '/monitoring', icon: Activity },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 flex-shrink-0 border-r border-slate-700 bg-slate-900 flex flex-col">
      <div className="flex items-center gap-2 p-4 h-16 border-b border-slate-700">
        <AppIcon size={24} className="w-6 h-6" />
        <h2 className="text-lg font-semibold text-slate-50">ВК Парсер</h2>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navigation.map((item) => {
          const isActive = (pathname ?? '').startsWith(item.href)
          const Icon = item.icon

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                isActive
                  ? 'bg-slate-800 text-slate-50'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-50'
              )}
            >
              <Icon className="mr-3 h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
        <div className="!mt-4 pt-4 border-t border-slate-700">
          <Link
            href="/settings"
            className={cn(
              'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
              pathname?.startsWith('/settings')
                ? 'bg-slate-800 text-slate-50'
                : 'text-slate-400 hover:bg-slate-800 hover:text-slate-50'
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
