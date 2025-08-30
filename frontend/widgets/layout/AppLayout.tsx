'use client'

import { AppSidebar } from '../sidebar/AppSidebar'
import { AppNavbar } from '../navbar/AppNavbar'
import {
 SidebarInset,
 SidebarProvider,
} from '@/shared/ui/sidebar'

interface AppLayoutProps {
 children: React.ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
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
