'use client'

import { usePathname } from 'next/navigation'
import { Bell, Circle, ChevronRight, Menu } from 'lucide-react'
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

  const pathSegments = pathname.split('/').filter(Boolean)
  const breadcrumbs = pathSegments.map((segment, index) => {
    const path = '/' + pathSegments.slice(0, index + 1).join('/')
    return {
      title: routeTitles[path] || segment,
      href: path,
      isLast: index === pathSegments.length - 1,
    }
  })

  return (
    <div className={cn('navbar bg-base-100 border-b', className)}>
      <div className="navbar-start">
        <label htmlFor="my-drawer-2" className="btn btn-ghost lg:hidden">
          <Menu />
        </label>
        <div className="text-sm breadcrumbs hidden sm:flex">
          <ul>
            <li>
              <a>Главная</a>
            </li>
            {breadcrumbs.map((breadcrumb) => (
              <li key={breadcrumb.href}>
                <a>{breadcrumb.title}</a>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className="navbar-end">
        <div className="flex items-center space-x-2 mr-4">
          <div className="badge badge-success badge-xs"></div>
          <span className="text-sm">API активно</span>
        </div>
        <div className="dropdown dropdown-end">
          <label tabIndex={0} className="btn btn-ghost btn-circle">
            <div className="indicator">
              <Bell size={20} />
              <span className="badge badge-xs badge-primary indicator-item">
                3
              </span>
            </div>
          </label>
          {/* Notifications dropdown content here */}
        </div>
        <div className="dropdown dropdown-end">
          <label tabIndex={0} className="btn btn-ghost btn-circle avatar">
            <div className="w-8 rounded-full bg-blue-100 ring ring-primary ring-offset-base-100 ring-offset-2">
              <span className="text-sm font-medium text-blue-700">А</span>
            </div>
          </label>
          <ul
            tabIndex={0}
            className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52"
          >
            <li>
              <a className="justify-between">
                Профиль
                <span className="badge">New</span>
              </a>
            </li>
            <li>
              <a>Настройки</a>
            </li>
            <li>
              <a>Выход</a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
