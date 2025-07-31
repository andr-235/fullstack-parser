import React from 'react'
import { Users } from 'lucide-react'
import type { GroupsHeaderProps } from '../../types'

export function GroupsHeader({
  title = 'Управление группами',
  description = 'Добавление, настройка и мониторинг VK групп для парсинга',
}: GroupsHeaderProps) {
  return (
    <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-xl p-4 text-white">
      <div className="flex items-center space-x-3 mb-2">
        <div className="p-2 bg-white/10 rounded-lg">
          <Users className="h-5 w-5" />
        </div>
        <h1 className="text-xl font-bold">{title}</h1>
      </div>
      <p className="text-slate-300 text-sm">{description}</p>
    </div>
  )
}
