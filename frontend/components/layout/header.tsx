'use client'

import { usePathname } from 'next/navigation'
import { ChevronRight, Bell, Circle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface HeaderProps {
  className?: string
}

const routeTitles: Record<string, string> = {
  '/dashboard': 'Дашборд',
  '/groups': 'VK Группы',
  '/keywords': 'Ключевые слова',
  '/comments': 'Комментарии',
  '/parser': 'Парсер',
  '/settings': 'Настройки',
}

export function Header({ className }: HeaderProps) {
  const pathname = usePathname()
  
  // Генерируем breadcrumbs из пути
  const pathSegments = pathname.split('/').filter(Boolean)
  const breadcrumbs = pathSegments.map((segment, index) => {
    const path = '/' + pathSegments.slice(0, index + 1).join('/')
    return {
      title: routeTitles[path] || segment,
      href: path,
      isLast: index === pathSegments.length - 1
    }
  })

  return (
    <header className={cn(
      "flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200",
      className
    )}>
      {/* Breadcrumbs */}
      <div className="flex items-center space-x-2">
        <nav className="flex items-center space-x-2 text-sm">
          <span className="text-gray-500">Главная</span>
          {breadcrumbs.map((breadcrumb, index) => (
            <div key={breadcrumb.href} className="flex items-center space-x-2">
              <ChevronRight size={16} className="text-gray-400" />
              <span
                className={cn(
                  breadcrumb.isLast
                    ? "text-gray-900 font-medium"
                    : "text-gray-500 hover:text-gray-700"
                )}
              >
                {breadcrumb.title}
              </span>
            </div>
          ))}
        </nav>
      </div>

      {/* Right side */}
      <div className="flex items-center space-x-4">
        {/* API Status */}
        <div className="flex items-center space-x-2">
          <Circle size={8} className="text-green-500 fill-current" />
          <span className="text-sm text-gray-600">API активно</span>
        </div>

        {/* Notifications */}
        <button className="relative p-2 rounded-lg hover:bg-gray-100">
          <Bell size={20} className="text-gray-600" />
          <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            3
          </span>
        </button>

        {/* User Menu */}
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
            <span className="text-sm font-medium text-blue-700">А</span>
          </div>
          <div className="hidden md:block">
            <p className="text-sm font-medium text-gray-900">Администратор</p>
            <p className="text-xs text-gray-500">admin@example.com</p>
          </div>
        </div>
      </div>
    </header>
  )
} 