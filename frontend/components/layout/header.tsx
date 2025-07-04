'use client'

import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { Bell, Menu, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

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

  const pathSegments = pathname.split('/').filter(Boolean)
  const breadcrumbs = pathSegments.map((segment, index) => {
    const path = '/' + pathSegments.slice(0, index + 1).join('/')
    return {
      title:
        routeTitles[path] || segment.charAt(0).toUpperCase() + segment.slice(1),
      href: path,
      isLast: index === pathSegments.length - 1,
    }
  })

  return (
    <header
      className={cn(
        'sticky top-0 z-10 flex h-16 w-full items-center justify-between border-b bg-white px-6 dark:bg-gray-950 dark:border-gray-800',
        className
      )}
    >
      <div className="flex items-center gap-4">
        {/* Mobile menu button can be added here if needed */}
        <nav className="hidden sm:flex items-center text-sm font-medium">
          <Link href="/dashboard" className="text-gray-500 hover:text-gray-900">
            Главная
          </Link>
          {breadcrumbs.map((breadcrumb, index) => (
            <div key={index} className="flex items-center">
              <ChevronRight className="h-4 w-4 mx-1 text-gray-400" />
              <Link
                href={breadcrumb.href}
                className={cn(
                  'hover:text-gray-900',
                  breadcrumb.isLast
                    ? 'text-gray-900 dark:text-white'
                    : 'text-gray-500 dark:text-gray-400'
                )}
              >
                {breadcrumb.title}
              </Link>
            </div>
          ))}
        </nav>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center space-x-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
          </span>
          <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
            API активно
          </span>
        </div>
        <Button variant="ghost" size="icon">
          <Bell className="h-5 w-5" />
          <span className="sr-only">Уведомления</span>
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="rounded-full w-8 h-8 bg-blue-100 hover:bg-blue-200 text-blue-800 font-semibold"
        >
          А
        </Button>
      </div>
    </header>
  )
}
