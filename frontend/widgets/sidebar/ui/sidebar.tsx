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
 Monitor,
} from 'lucide-react'
import { cn } from '@/shared/lib/utils'

const navigation = [
 { name: 'Дашборд', href: '/dashboard', icon: BarChart3 },
 { name: 'VK Группы', href: '/groups', icon: Users },
 { name: 'Ключевые слова', href: '/keywords', icon: KeyRound },
 { name: 'Комментарии', href: '/comments', icon: MessageSquare },
 { name: 'Парсер', href: '/parser', icon: Play },
 { name: 'Мониторинг', href: '/monitoring', icon: Activity },
 { name: 'Настройки', href: '/settings', icon: Settings },
]

interface SidebarProps {
 className?: string
}

export function Sidebar({ className }: SidebarProps) {
 const pathname = usePathname()

 return (
  <aside className={cn(
   'w-64 flex-shrink-0 border-r border-border bg-card flex flex-col',
   className
  )}>
   <div className="p-6 border-b border-border">
    <h2 className="text-lg font-semibold text-foreground">VK Parser</h2>
    <p className="text-sm text-muted-foreground">Панель управления</p>
   </div>

   <nav className="flex-1 p-4 space-y-2">
    {navigation.map((item) => {
     const isActive = pathname === item.href
     return (
      <Link
       key={item.name}
       href={item.href}
       className={cn(
        'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
        isActive
         ? 'bg-primary text-primary-foreground'
         : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
       )}
      >
       <item.icon className="h-4 w-4" />
       {item.name}
      </Link>
     )
    })}
   </nav>

   <div className="p-4 border-t border-border">
    <div className="text-xs text-muted-foreground text-center">
     VK Parser v1.0
    </div>
   </div>
  </aside>
 )
}
