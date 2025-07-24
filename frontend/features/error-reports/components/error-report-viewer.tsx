'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/shared/ui/collapsible'
import { Alert, AlertDescription } from '@/shared/ui/alert'
import { Separator } from '@/shared/ui/separator'
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  ChevronDown,
  ChevronRight,
  Info,
  XCircle,
  Zap,
} from 'lucide-react'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

interface ErrorEntry {
  timestamp: string
  error_type:
    | 'validation'
    | 'database'
    | 'api'
    | 'network'
    | 'authentication'
    | 'authorization'
    | 'rate_limit'
    | 'timeout'
    | 'unknown'
  severity: 'low' | 'medium' | 'high' | 'critical'
  message: string
  details?: string
  context?: {
    user_id?: number
    group_id?: number
    vk_id?: number
    screen_name?: string
    operation?: string
    additional_data?: Record<string, any>
  }
  stack_trace?: string
}

interface ErrorReport {
  report_id: string
  created_at: string
  operation: string
  total_errors: number
  errors: ErrorEntry[]
  summary: Record<string, number>
  recommendations: string[]
  groups_processed?: number
  groups_successful?: number
  groups_failed?: number
  groups_skipped?: number
  processing_time_seconds?: number
}

interface ErrorReportViewerProps {
  report: ErrorReport
  onAcknowledge?: (reportId: string) => void
  onDismiss?: (reportId: string) => void
}

const severityColors = {
  low: 'bg-blue-100 text-blue-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800',
}

const severityIcons = {
  low: Info,
  medium: AlertTriangle,
  high: XCircle,
  critical: Zap,
}

const errorTypeLabels = {
  validation: 'Валидация',
  database: 'База данных',
  api: 'API',
  network: 'Сеть',
  authentication: 'Аутентификация',
  authorization: 'Авторизация',
  rate_limit: 'Лимит запросов',
  timeout: 'Таймаут',
  unknown: 'Неизвестно',
}

export function ErrorReportViewer({
  report,
  onAcknowledge,
  onDismiss,
}: ErrorReportViewerProps) {
  const [expandedErrors, setExpandedErrors] = useState<Set<string>>(new Set())

  const toggleError = (index: number) => {
    const newExpanded = new Set(expandedErrors)
    const key = index.toString()
    if (newExpanded.has(key)) {
      newExpanded.delete(key)
    } else {
      newExpanded.add(key)
    }
    setExpandedErrors(newExpanded)
  }

  const formatTimestamp = (timestamp: string) => {
    return format(new Date(timestamp), 'dd.MM.yyyy HH:mm:ss', { locale: ru })
  }

  const getSeverityIcon = (severity: ErrorEntry['severity']) => {
    const Icon = severityIcons[severity]
    return <Icon className="w-4 h-4" />
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CardTitle className="text-lg">Отчет об ошибках</CardTitle>
            <Badge variant="outline" className="text-xs">
              {report.report_id.slice(0, 8)}...
            </Badge>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="w-4 h-4" />
            {formatTimestamp(report.created_at)}
          </div>
        </div>

        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="font-medium">Операция:</span>
            <span className="text-muted-foreground">{report.operation}</span>
          </div>

          {report.processing_time_seconds && (
            <div className="flex items-center gap-2">
              <span className="font-medium">Время обработки:</span>
              <span className="text-muted-foreground">
                {report.processing_time_seconds.toFixed(2)}с
              </span>
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Статистика */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 bg-muted rounded-lg">
            <div className="text-2xl font-bold text-red-600">
              {report.total_errors}
            </div>
            <div className="text-sm text-muted-foreground">Всего ошибок</div>
          </div>

          {report.groups_processed !== undefined && (
            <>
              <div className="text-center p-3 bg-muted rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {report.groups_processed}
                </div>
                <div className="text-sm text-muted-foreground">Обработано</div>
              </div>
              <div className="text-center p-3 bg-muted rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {report.groups_successful}
                </div>
                <div className="text-sm text-muted-foreground">Успешно</div>
              </div>
              <div className="text-center p-3 bg-muted rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {report.groups_failed}
                </div>
                <div className="text-sm text-muted-foreground">С ошибками</div>
              </div>
            </>
          )}
        </div>

        {/* Рекомендации */}
        {report.recommendations.length > 0 && (
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>
              <div className="font-medium mb-2">
                Рекомендации по исправлению:
              </div>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {report.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </AlertDescription>
          </Alert>
        )}

        {/* Список ошибок */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold">Детали ошибок</h3>

          {report.errors.map((error, index) => (
            <Collapsible key={index}>
              <CollapsibleTrigger asChild>
                <Button
                  variant="ghost"
                  className="w-full justify-between p-4 h-auto"
                  onClick={() => toggleError(index)}
                >
                  <div className="flex items-center gap-3 text-left">
                    {getSeverityIcon(error.severity)}
                    <div className="flex flex-col items-start">
                      <span className="font-medium">{error.message}</span>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Badge className={severityColors[error.severity]}>
                          {errorTypeLabels[error.error_type]}
                        </Badge>
                        <Badge variant="outline">{error.severity}</Badge>
                        <span>{formatTimestamp(error.timestamp)}</span>
                      </div>
                    </div>
                  </div>
                  {expandedErrors.has(index.toString()) ? (
                    <ChevronDown className="w-4 h-4" />
                  ) : (
                    <ChevronRight className="w-4 h-4" />
                  )}
                </Button>
              </CollapsibleTrigger>

              <CollapsibleContent className="px-4 pb-4">
                <div className="space-y-3">
                  {error.details && (
                    <div>
                      <div className="font-medium text-sm mb-1">Детали:</div>
                      <div className="text-sm text-muted-foreground bg-muted p-3 rounded">
                        {error.details}
                      </div>
                    </div>
                  )}

                  {error.context && (
                    <div>
                      <div className="font-medium text-sm mb-1">Контекст:</div>
                      <div className="text-sm text-muted-foreground bg-muted p-3 rounded">
                        <pre className="whitespace-pre-wrap">
                          {JSON.stringify(error.context, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}

                  {error.stack_trace && (
                    <div>
                      <div className="font-medium text-sm mb-1">
                        Stack Trace:
                      </div>
                      <div className="text-xs text-muted-foreground bg-muted p-3 rounded max-h-40 overflow-auto">
                        <pre className="whitespace-pre-wrap">
                          {error.stack_trace}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              </CollapsibleContent>
            </Collapsible>
          ))}
        </div>

        {/* Действия */}
        <Separator />

        <div className="flex justify-end gap-2">
          {onDismiss && (
            <Button
              variant="outline"
              onClick={() => onDismiss(report.report_id)}
            >
              Закрыть
            </Button>
          )}
          {onAcknowledge && (
            <Button onClick={() => onAcknowledge(report.report_id)}>
              Подтвердить обработку
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
