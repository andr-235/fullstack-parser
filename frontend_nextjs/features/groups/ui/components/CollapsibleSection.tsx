import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { ChevronDown, ChevronUp } from 'lucide-react'
import type { CollapsibleSectionProps } from '../../types'

export function CollapsibleSection({
  title,
  icon: Icon,
  children,
  defaultExpanded = false,
}: CollapsibleSectionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  return (
    <Card className="border-slate-700 bg-slate-800 shadow-lg">
      <CardHeader
        className="pb-3 cursor-pointer hover:bg-slate-750 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Icon className="h-4 w-4 text-slate-400" />
            <CardTitle className="text-sm font-semibold text-slate-200">
              {title}
            </CardTitle>
          </div>
          {isExpanded ? (
            <ChevronUp className="h-4 w-4 text-slate-400" />
          ) : (
            <ChevronDown className="h-4 w-4 text-slate-400" />
          )}
        </div>
      </CardHeader>
      {isExpanded && <CardContent className="pt-0">{children}</CardContent>}
    </Card>
  )
}
