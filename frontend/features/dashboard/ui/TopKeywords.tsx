'use client'

import { Hash, ExternalLink, TrendingUp, Target, BarChart3 } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Progress } from '@/shared/ui'

import { DashboardTopItem } from '@/entities/dashboard'

interface TopKeywordsProps {
  keywords: DashboardTopItem[]
}

export function TopKeywords({ keywords }: TopKeywordsProps) {
  // Находим максимальное значение для расчета прогресса
  const maxCount = keywords.length > 0 ? Math.max(...keywords.map(k => k.count)) : 0

  if (keywords.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Hash className="h-5 w-5" />
            Популярные ключевые слова
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <Hash className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">Данные о ключевых словах недоступны</p>
            <p className="text-sm text-muted-foreground">
              Ключевые слова появятся здесь после анализа комментариев
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5" />
          Популярные ключевые слова
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {keywords.slice(0, 8).map((keyword, index) => {
            const progressValue = maxCount > 0 ? (keyword.count / maxCount) * 100 : 0
            const isHot = index < 3

            return (
              <div
                key={index}
                className="flex items-center gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10">
                  <span className="text-xs font-medium text-primary">{index + 1}</span>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge
                        variant={isHot ? 'default' : 'secondary'}
                        className="font-medium text-xs"
                      >
                        {keyword.name}
                      </Badge>
                      {isHot && (
                        <Badge variant="destructive" className="text-xs">
                          <TrendingUp className="h-3 w-3 mr-1" />
                          Горячий
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <Target className="h-3 w-3" />
                      <span className="text-xs font-medium">{keyword.count}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Progress value={progressValue} className="flex-1 h-2" />
                    <span className="text-xs text-muted-foreground min-w-[3rem]">
                      {progressValue.toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {keywords.length > 8 && (
          <div className="mt-4 pt-4 border-t">
            <p className="text-sm text-muted-foreground mb-3">
              И ещё {keywords.length - 8} ключевых слов
            </p>
            <Button variant="outline" className="w-full">
              Показать все ключевые слова
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
