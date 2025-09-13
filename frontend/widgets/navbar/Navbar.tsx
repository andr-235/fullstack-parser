'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { memo, useMemo, useState } from 'react'

import { Bell, Search, Menu, X } from 'lucide-react'
import { useAuthStore } from '@/entities/user/model/auth-store'
import { UserMenu } from '@/widgets/auth/ui/UserMenu'

interface NavbarProps {
  notificationCount?: number
}

interface BreadcrumbItem {
  label: string
  href: string
  isLast: boolean
}

const PAGE_TRANSLATIONS: Record<string, string> = {
  dashboard: 'Панель управления',
  comments: 'Комментарии',
  groups: 'Группы',
  keywords: 'Ключевые слова',
  monitoring: 'Мониторинг',
  parser: 'Парсер',
  settings: 'Настройки',
} as const

export const Navbar = memo(({ notificationCount = 0 }: NavbarProps) => {
  const pathname = usePathname()
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const { user, isAuthenticated } = useAuthStore()

  const breadcrumbs = useMemo((): BreadcrumbItem[] => {
    const segments = pathname.split('/').filter(Boolean)
    
    return segments.map((segment, index) => {
      const href = '/' + segments.slice(0, index + 1).join('/')
      const label = PAGE_TRANSLATIONS[segment.toLowerCase()] || 
        segment.charAt(0).toUpperCase() + segment.slice(1)

      return {
        label,
        href,
        isLast: index === segments.length - 1,
      }
    })
  }, [pathname])


  return (
    <header className="bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 border-b border-white/20 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Left section */}
          <div className="flex items-center space-x-4">
            {/* Mobile menu button */}
            <button 
              className="p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 lg:hidden"
              aria-label="Toggle sidebar"
            >
              <Menu className="h-5 w-5" />
            </button>
            
            {/* Logo/Brand */}
            <div className="flex items-center">
              <div className="h-8 w-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">A</span>
              </div>
              <span className="ml-2 text-xl font-semibold text-white hidden sm:block">
                Analytics
              </span>
            </div>
            
            {/* Breadcrumbs */}
            <nav className="hidden lg:flex items-center space-x-1 text-sm">
              {breadcrumbs.map((breadcrumb, index) => (
                <div key={breadcrumb.href} className="flex items-center">
                  {index > 0 && (
                    <svg className="h-4 w-4 mx-2 text-white/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  )}
                  {breadcrumb.isLast ? (
                    <span className="font-medium text-white">
                      {breadcrumb.label}
                    </span>
                  ) : (
                    <Link 
                      href={breadcrumb.href}
                      className="text-white/70 hover:text-white transition-colors duration-200"
                    >
                      {breadcrumb.label}
                    </Link>
                  )}
                </div>
              ))}
            </nav>
          </div>

          {/* Right section */}
          <div className="flex items-center space-x-2">
            {/* Search */}
            <div className="relative hidden md:block">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-white/50" />
                <input 
                  type="search" 
                  placeholder="Поиск..." 
                  className="w-64 lg:w-80 pl-10 pr-4 py-2 border border-white/20 rounded-lg bg-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all duration-200 backdrop-blur-sm"
                />
              </div>
            </div>

            {/* Mobile search button */}
            <button 
              className="p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 md:hidden"
              onClick={() => setIsSearchOpen(!isSearchOpen)}
              aria-label="Search"
            >
              <Search className="h-5 w-5" />
            </button>


            {/* Notifications */}
            <button 
              className="relative p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-colors duration-200"
              aria-label="Notifications"
            >
              <Bell className="h-5 w-5" />
              {notificationCount > 0 && (
                <span className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center rounded-full bg-red-500 text-white text-xs font-medium min-w-[20px]">
                  {notificationCount > 99 ? '99+' : notificationCount}
                </span>
              )}
            </button>

            {/* User menu */}
            {isAuthenticated && user ? (
              <div className="ml-2">
                <UserMenu />
              </div>
            ) : (
              <div className="ml-2">
                <Link 
                  href="/login"
                  className="flex items-center space-x-2 px-3 py-2 rounded-lg text-white/80 hover:text-white hover:bg-white/10 transition-colors duration-200"
                >
                  <div className="h-8 w-8 bg-white/20 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-white">U</span>
                  </div>
                  <span className="hidden lg:block text-sm font-medium">
                    Войти
                  </span>
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Mobile search */}
        {isSearchOpen && (
          <div className="md:hidden py-4 border-t border-white/20">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-white/50" />
              <input 
                type="search" 
                placeholder="Поиск..." 
                className="w-full pl-10 pr-4 py-2 border border-white/20 rounded-lg bg-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent backdrop-blur-sm"
                autoFocus
              />
              <button 
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/50 hover:text-white"
                onClick={() => setIsSearchOpen(false)}
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  )
})
