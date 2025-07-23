import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Users, Activity, Pause } from 'lucide-react'
import { CollapsibleSection } from './CollapsibleSection'
import type { GroupsStatsData } from '../../types'

export function GroupsStats({
  totalGroups,
  activeGroups,
  inactiveGroups,
}: GroupsStatsData) {
  return (
    <CollapsibleSection title="Статистика" icon={Users} defaultExpanded={false}>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <Users className="h-4 w-4 text-blue-400" />
              </div>
              <div>
                <p className="text-xs font-medium text-slate-300">
                  Всего групп
                </p>
                <p className="text-lg font-bold text-blue-400">{totalGroups}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <Activity className="h-4 w-4 text-green-400" />
              </div>
              <div>
                <p className="text-xs font-medium text-slate-300">Активных</p>
                <p className="text-lg font-bold text-green-400">
                  {activeGroups}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <Pause className="h-4 w-4 text-orange-400" />
              </div>
              <div>
                <p className="text-xs font-medium text-slate-300">Неактивных</p>
                <p className="text-lg font-bold text-orange-400">
                  {inactiveGroups}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </CollapsibleSection>
  )
}
