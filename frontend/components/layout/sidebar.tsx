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
  Menu,
  X
} from 'lucide-react'

const navigation = [
  { name: 'Дашборд', href: '/dashboard', icon: BarChart3 },
  { name: 'VK Группы', href: '/groups', icon: Users },
  { name: 'Ключевые слова', href: '/keywords', icon: KeyRound },
  { name: 'Комментарии', href: '/comments', icon: MessageSquare },
  { name: 'Парсер', href: '/parser', icon: Play },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="bg-base-100 w-80 min-h-full">
        <div className="flex items-center gap-2 p-4 border-b">
          <div className="text-2xl">📊</div>
            <h2 className="text-lg font-semibold">
              VK Parser
            </h2>
        </div>

      <ul className="menu p-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <li key={item.name}>
              <Link
                href={item.href}
                className={`${isActive ? 'active' : ''}`}
              >
                <Icon size={20} />
                {item.name}
              </Link>
            </li>
          )
        })}
        <div className="divider"></div>
        <li>
          <Link href="/settings" className={pathname === '/settings' ? 'active' : ''}>
            <Settings size={20} />
            Настройки
          </Link>
        </li>
      </ul>
    </div>
  )
} 