'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

import { Bell, Search } from 'lucide-react'

import { Badge } from '@/shared/ui/badge'
import {
 Breadcrumb,
 BreadcrumbItem,
 BreadcrumbLink,
 BreadcrumbList,
 BreadcrumbPage,
 BreadcrumbSeparator,
} from '@/shared/ui/breadcrumb'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Separator } from '@/shared/ui/separator'
import {
 SidebarTrigger,
} from '@/shared/ui/sidebar'
import { ThemeToggle } from '@/shared/ui/theme-toggle'

interface NavbarProps {
 notificationCount?: number
}

export function Navbar({ notificationCount = 0 }: NavbarProps) {
 const pathname = usePathname()

 // Generate breadcrumbs from pathname
 const generateBreadcrumbs = () => {
  const segments = pathname.split('/').filter(Boolean)
  const breadcrumbs = []

  for (let i = 0; i < segments.length; i++) {
   const segment = segments[i]
   if (!segment) continue

   const href = '/' + segments.slice(0, i + 1).join('/')
   let label = segment.charAt(0).toUpperCase() + segment.slice(1)

   // Translate common page names
   switch (segment.toLowerCase()) {
    case 'dashboard':
     label = 'Панель управления'
     break
    case 'comments':
     label = 'Комментарии'
     break
    case 'groups':
     label = 'Группы'
     break
    case 'keywords':
     label = 'Ключевые слова'
     break
    case 'monitoring':
     label = 'Мониторинг'
     break
    case 'parser':
     label = 'Парсер'
     break
    case 'settings':
     label = 'Настройки'
     break
    default:
     break
   }

   breadcrumbs.push({
    label,
    href,
    isLast: i === segments.length - 1,
   })
  }

  return breadcrumbs
 }

 const breadcrumbs = generateBreadcrumbs()

 return (
  <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
   <div className="flex items-center gap-2 px-4">
    <SidebarTrigger className="-ml-1" />
    <Separator orientation="vertical" className="mr-2 h-4" />
    <Breadcrumb>
     <BreadcrumbList>
      {breadcrumbs.map((breadcrumb, index) => (
       <div key={breadcrumb.href} className="flex items-center">
        {index > 0 && <BreadcrumbSeparator className="hidden md:block" />}
        <BreadcrumbItem className="hidden md:block">
         {breadcrumb.isLast ? (
          <BreadcrumbPage>{breadcrumb.label}</BreadcrumbPage>
         ) : (
          <BreadcrumbLink asChild>
           <Link href={breadcrumb.href}>{breadcrumb.label}</Link>
          </BreadcrumbLink>
         )}
        </BreadcrumbItem>
       </div>
      ))}
     </BreadcrumbList>
    </Breadcrumb>
   </div>

   <div className="ml-auto flex items-center gap-2 px-4">
    {/* Search */}
    <div className="relative hidden md:block">
     <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
     <Input
      type="search"
      placeholder="Поиск..."
      className="w-[200px] pl-8 lg:w-[300px]"
     />
    </div>

    {/* Theme Toggle */}
    <ThemeToggle />

    {/* Notifications */}
    <Button variant="outline" size="icon" className="relative">
     <Bell className="h-4 w-4" />
     {notificationCount > 0 && (
      <Badge
       variant="destructive"
       className="absolute -top-2 -right-2 h-5 w-5 flex items-center justify-center p-0 text-xs"
      >
       {notificationCount > 99 ? '99+' : notificationCount}
      </Badge>
     )}
    </Button>
   </div>
  </header>
 )
}
