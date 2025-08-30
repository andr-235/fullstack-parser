'use client'

import { ChevronRight, type LucideIcon } from 'lucide-react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'

import {
 Collapsible,
 CollapsibleContent,
 CollapsibleTrigger,
} from '@/shared/ui/collapsible'
import {
 SidebarGroup,
 SidebarGroupLabel,
 SidebarMenu,
 SidebarMenuButton,
 SidebarMenuItem,
 SidebarMenuSub,
 SidebarMenuSubButton,
 SidebarMenuSubItem,
} from '@/shared/ui/sidebar'

export function NavMain({
 items,
}: {
 items: {
  title: string
  url: string
  icon?: LucideIcon
  isActive?: boolean
  badge?: React.ReactNode
  items?: {
   title: string
   url: string
  }[]
 }[]
}) {
 const pathname = usePathname()

 return (
  <SidebarGroup>
   <SidebarGroupLabel>Платформа</SidebarGroupLabel>
   <SidebarMenu>
    {items.map((item) => (
     <Collapsible
      key={item.title}
      asChild
      defaultOpen={item.isActive ?? false}
      className="group/collapsible"
     >
      <SidebarMenuItem>
       <CollapsibleTrigger asChild>
        <SidebarMenuButton
         asChild
         tooltip={item.title}
         isActive={pathname === item.url}
        >
         <Link href={item.url}>
          {item.icon && <item.icon />}
          <span>{item.title}</span>
          {item.badge}
         </Link>
        </SidebarMenuButton>
       </CollapsibleTrigger>
       {item.items?.length ? (
        <CollapsibleContent>
         <SidebarMenuSub>
          {item.items?.map((subItem) => (
           <SidebarMenuSubItem key={subItem.title}>
            <SidebarMenuSubButton asChild isActive={pathname === subItem.url}>
             <Link href={subItem.url}>
              <span>{subItem.title}</span>
             </Link>
            </SidebarMenuSubButton>
           </SidebarMenuSubItem>
          ))}
         </SidebarMenuSub>
        </CollapsibleContent>
       ) : null}
      </SidebarMenuItem>
     </Collapsible>
    ))}
   </SidebarMenu>
  </SidebarGroup>
 )
}
