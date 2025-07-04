'use client'

import { useState } from 'react'
import {
  useParserState,
  useRecentRuns,
  useParserStats,
  useStartParser,
  useStopParser,
} from '@/hooks/use-parser'
import { useGroups } from '@/hooks/use-groups'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Badge, BadgeProps } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { formatDuration, formatRelativeTime } from '@/lib/utils'
import {
  Play,
  Square,
  Clock,
  Activity,
  AlertCircle,
  CheckCircle,
  Info,
  RefreshCw,
  BarChart,
  History,
  HardDrive,
} from 'lucide-react'

const StatusInfo = ({
  status,
}: {
  status: 'running' | 'completed' | 'failed' | 'stopped'
}) => {
  const statusConfig: {
    [key in typeof status]: {
      icon: JSX.Element
      label: string
      variant: BadgeProps['variant']
    }
  } = {
    running: {
      icon: <Activity className="h-4 w-4 text-blue-500" />,
      label: 'Выполняется',
      variant: 'default',
    },
    completed: {
      icon: <CheckCircle className="h-4 w-4 text-green-500" />,
      label: 'Завершено',
      variant: 'secondary',
    },
    failed: {
      icon: <AlertCircle className="h-4 w-4 text-destructive" />,
      label: 'Ошибка',
      variant: 'destructive',
    },
    stopped: {
      icon: <Info className="h-4 w-4 text-muted-foreground" />,
      label: 'Остановлен',
      variant: 'outline',
    },
  }
  const config = statusConfig[status] || statusConfig.stopped
  return (
    <Badge variant={config.variant} className="flex items-center gap-1.5">
      {config.icon}
      <span>{config.label}</span>
    </Badge>
  )
}

export default function ParserPage() {
  const [selectedGroup, setSelectedGroup] = useState<string | undefined>()

  const {
    data: state,
    isLoading: isLoadingState,
    refetch: refetchState,
  } = useParserState()
  const { data: stats, isLoading: isLoadingStats } = useParserStats()
  const { data: runs, isLoading: isLoadingRuns } = useRecentRuns()
  const { data: groups } = useGroups({})

  const startParser = useStartParser()
  const stopParser = useStopParser()

  const handleStart = () => {
    if (selectedGroup) {
      startParser.mutate({ group_id: Number(selectedGroup) })
    }
  }

  const handleStop = () => {
    stopParser.mutate()
  }

  const isLoading =
    isLoadingState || startParser.isPending || stopParser.isPending

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HardDrive /> Управление парсером
          </CardTitle>
          <CardDescription>
            Запуск и мониторинг процесса сбора комментариев.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h3 className="font-semibold text-muted-foreground">Статус</h3>
            <div className="flex items-center gap-4">
              {isLoadingState ? (
                <LoadingSpinner />
              ) : (
                <StatusInfo status={state?.status || 'stopped'} />
              )}
            </div>
            <h3 className="font-semibold text-muted-foreground pt-4">Запуск</h3>
            <div className="flex gap-4">
              <Select
                value={selectedGroup}
                onValueChange={setSelectedGroup}
                disabled={state?.status === 'running'}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Выберите группу для парсинга" />
                </SelectTrigger>
                <SelectContent>
                  {groups?.items.map((g) => (
                    <SelectItem key={g.id} value={String(g.id)}>
                      {g.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {state?.status !== 'running' ? (
                <Button
                  onClick={handleStart}
                  disabled={!selectedGroup || startParser.isPending}
                >
                  <Play className="h-4 w-4 mr-2" />
                  Запустить
                </Button>
              ) : (
                <Button
                  variant="destructive"
                  onClick={handleStop}
                  disabled={stopParser.isPending}
                >
                  <Square className="h-4 w-4 mr-2" />
                  Остановить
                </Button>
              )}
            </div>
          </div>
          <div className="space-y-4">
            <h3 className="font-semibold text-muted-foreground">
              Текущая задача
            </h3>
            {state?.status === 'running' && state.task ? (
              <div className="p-4 bg-muted/50 rounded-lg">
                <p>
                  <strong>Группа:</strong> {state.task.group_name}
                </p>
                <p>
                  <strong>Прогресс:</strong> {state.task.progress.toFixed(2)}%
                </p>
                <p>
                  <strong>Обработано постов:</strong>{' '}
                  {state.task.posts_processed}
                </p>
              </div>
            ) : (
              <p className="text-muted-foreground italic">Нет активных задач</p>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History /> Недавние запуски
            </CardTitle>
            <Button variant="ghost" size="icon" onClick={() => refetchState()}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </CardHeader>
          <CardContent>
            {isLoadingRuns ? (
              <LoadingSpinner />
            ) : (
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Статус</TableHead>
                      <TableHead>Группа</TableHead>
                      <TableHead>Длительность</TableHead>
                      <TableHead>Ошибки</TableHead>
                      <TableHead>Время</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {runs?.items.map((run) => (
                      <TableRow key={run.task_id}>
                        <TableCell>
                          <StatusInfo status={run.status} />
                        </TableCell>
                        <TableCell>{run.group_name || 'N/A'}</TableCell>
                        <TableCell>
                          {run.stats?.duration_seconds
                            ? formatDuration(run.stats.duration_seconds)
                            : '-'}
                        </TableCell>
                        <TableCell>
                          {run.error_message ? (
                            <span className="text-destructive">Да</span>
                          ) : (
                            'Нет'
                          )}
                        </TableCell>
                        <TableCell>
                          {formatRelativeTime(run.started_at)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart /> Общая статистика
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoadingStats ? (
              <LoadingSpinner />
            ) : (
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Всего запусков</span>
                  <strong>{stats?.total_runs}</strong>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">
                    Успешных запусков
                  </span>
                  <strong>{stats?.successful_runs}</strong>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">
                    Среднее время (сек)
                  </span>
                  <strong>
                    {stats?.average_duration
                      ? stats.average_duration.toFixed(2)
                      : 0}
                  </strong>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">
                    Постов обработано
                  </span>
                  <strong>{stats?.total_posts_processed}</strong>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">
                    Комментариев найдено
                  </span>
                  <strong>{stats?.total_comments_found}</strong>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
