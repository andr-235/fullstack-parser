'use client'

import { useRouteAccess } from '@/shared/hooks/useRouteAccess'
import { SidebarInset, SidebarProvider } from '@/shared/ui/sidebar'
import { AppNavbar } from '../navbar/AppNavbar'
import { AppSidebar } from '../sidebar'

interface AppLayoutProps {
  children: React.ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const { isAuthenticated, isLoading } = useRouteAccess()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-sm text-muted-foreground">Загрузка...</p>
        </div>
      </div>
    )
  }

  if (isAuthenticated) {
    // Приватный layout с sidebar и navbar
    return (
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset>
          <AppNavbar />
          <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
            {children}
          </div>
        </SidebarInset>
      </SidebarProvider>
    )
  }

  // Публичный layout без sidebar и navbar
  return (
    <div className="min-h-screen bg-gray-50">
      {children}
    </div>
  )
}
