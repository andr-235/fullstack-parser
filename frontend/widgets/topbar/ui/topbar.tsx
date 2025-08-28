'use client'

import { Bell, Search, User } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/shared/ui/avatar'
import { Badge } from '@/shared/ui/badge'
import { ThemeToggle } from '@/shared/ui/theme-toggle'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/shared/ui/dropdown-menu'
import { Input } from '@/shared/ui/input'
import { cn } from '@/shared/lib/utils'

interface TopbarProps {
 className?: string
}

export function Topbar({ className }: TopbarProps) {
 // Временные данные для демонстрации
 const user = {
  name: 'Администратор',
  email: 'admin@vkparser.com',
  avatar: '/avatar-placeholder.png'
 }

 const notifications = 3 // Количество уведомлений

 return (
  <header className={cn(
   'h-16 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 flex items-center justify-between px-6',
   className
  )}>
   {/* Левая часть - поиск */}
   <div className="flex items-center gap-4 flex-1">
    <div className="relative max-w-sm">
     <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
     <Input
      placeholder="Поиск..."
      className="pl-10 bg-background border-border"
     />
    </div>
   </div>

   {/* Правая часть - действия */}
   <div className="flex items-center gap-2">
    {/* Переключатель темы */}
    <ThemeToggle />

    {/* Уведомления */}
    <Button variant="ghost" size="icon" className="relative">
     <Bell className="h-5 w-5" />
     {notifications > 0 && (
      <Badge
       variant="destructive"
       className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
      >
       {notifications}
      </Badge>
     )}
    </Button>

    {/* Меню пользователя */}
    <DropdownMenu>
     <DropdownMenuTrigger asChild>
      <Button variant="ghost" className="relative h-10 w-10 rounded-full">
       <Avatar className="h-10 w-10">
        <AvatarImage src={user.avatar} alt={user.name} />
        <AvatarFallback>
         <User className="h-5 w-5" />
        </AvatarFallback>
       </Avatar>
      </Button>
     </DropdownMenuTrigger>
     <DropdownMenuContent className="w-56" align="end" forceMount>
      <DropdownMenuLabel className="font-normal">
       <div className="flex flex-col space-y-1">
        <p className="text-sm font-medium leading-none">{user.name}</p>
        <p className="text-xs leading-none text-muted-foreground">
         {user.email}
        </p>
       </div>
      </DropdownMenuLabel>
      <DropdownMenuSeparator />
      <DropdownMenuItem>
       Профиль
      </DropdownMenuItem>
      <DropdownMenuItem>
       Настройки
      </DropdownMenuItem>
      <DropdownMenuSeparator />
      <DropdownMenuItem>
       Выйти
      </DropdownMenuItem>
     </DropdownMenuContent>
    </DropdownMenu>
   </div>
  </header>
 )
}
