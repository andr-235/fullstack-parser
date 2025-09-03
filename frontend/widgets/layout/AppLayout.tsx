'use client'

import {
 SidebarInset,
 SidebarProvider,
} from '@/shared/ui/sidebar'

import { AppNavbar } from '../navbar/AppNavbar'
import { AppSidebar } from '../sidebar/AppSidebar'

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
