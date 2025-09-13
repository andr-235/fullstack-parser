'use client'

import { useRouteAccess } from '@/shared/hooks/useRouteAccess'
import { SidebarInset, SidebarProvider } from '@/shared/ui/sidebar'
import { GlassLayout } from '@/shared/ui/glass-layout'
import { AppNavbar } from '../navbar/AppNavbar'
import { AppSidebar } from '../sidebar'

interface AppLayoutProps {
  children: React.ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const { isAuthenticated, isLoading } = useRouteAccess()

  if (isLoading) {
    return (
      <GlassLayout variant="minimal">
        <div className="flex items-center justify-center min-h-screen">
          <div className="flex flex-col items-center space-y-4">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-white/50 border-t-transparent" />
            <p className="text-sm text-white/70">Загрузка...</p>
          </div>
        </div>
      </GlassLayout>
    )
  }

  if (isAuthenticated) {
    // Приватный layout с sidebar и navbar
    return (
      <GlassLayout variant="content">
        <SidebarProvider>
          <AppSidebar />
          <SidebarInset>
            <AppNavbar />
            <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
              {children}
            </div>
          </SidebarInset>
        </SidebarProvider>
      </GlassLayout>
    )
  }

  // Публичный layout без sidebar и navbar
  return (
    <GlassLayout variant="minimal">
      {children}
    </GlassLayout>
  )
}
