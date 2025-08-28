'use client'

import { ReactNode } from 'react'

interface LayoutProps {
 children: ReactNode
 header?: ReactNode
 sidebar?: ReactNode
 footer?: ReactNode
}

export function Layout({ children, header, sidebar, footer }: LayoutProps) {
 return (
  <div className="min-h-screen bg-background">
   {header && <header className="border-b">{header}</header>}

   <div className="flex">
    {sidebar && (
     <aside className="w-64 border-r bg-muted/40">
      {sidebar}
     </aside>
    )}

    <main className="flex-1 p-6">
     {children}
    </main>
   </div>

   {footer && <footer className="border-t">{footer}</footer>}
  </div>
 )
}
