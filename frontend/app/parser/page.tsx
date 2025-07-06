'use client'

import React, { useState } from 'react'
import {
  useParserState,
  useParserStats,
  useStartParser,
  useStopParser,
  useRecentRuns,
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
import {
  Play,
  Pause,
  Server,
  Timer,
  CheckCircle2,
  XCircle,
  History,
} from 'lucide-react'
import { Progress } from '@/components/ui/progress'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import type { ParseTaskResponse } from '@/types/api'

const statusConfig: Record<
  string,
  { label: string; variant: BadgeProps['variant']; icon: React.ElementType }
> = {
  running: { label: 'В работе', variant: 'success', icon: Play },
  completed: { label: 'Завершен', variant: 'default', icon: CheckCircle2 },
  failed: { label: 'Ошибка', variant: 'destructive', icon: XCircle },
  stopped: { label: 'Остановлен', variant: 'secondary', icon: Pause },
}

const ParserStatus = ({ status }: { status: string }) => {
  const config = statusConfig[status] || statusConfig.stopped
  return (
    <Badge variant={config.variant} className="flex items-center gap-1.5">
      <config.icon className="h-3 w-3" />
      <span>{config.label}</span>
    </Badge>
  )
}

export default function ParserPage() {
  const [selectedGroupId, setSelectedGroupId] = useState<string>('')
  const { data: state, isLoading: isLoadingState } = useParserState()
  const { data: stats, isLoading: isLoadingStats } = useParserStats()
  const { data: history, isLoading: isLoadingHistory } = useRecentRuns()
  const { data: groupsData } = useGroups()
  const startParserMutation = useStartParser()
  const stopParserMutation = useStopParser()

  const handleStart = () => {
    if (selectedGroupId) {
      startParserMutation.mutate({ group_id: Number(selectedGroupId) })
    }
  }

  const isActionInProgress =
    isLoadingState ||
    startParserMutation.isPending ||
    stopParserMutation.isPending

  const groups = groupsData?.items || []

  return (
    <div className="grid gap-6 md:grid-cols-3">
      {/* Control Panel */}
      <div className="md:col-span-1 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Управление парсером</CardTitle>
            <CardDescription>
              Запустите или остановите процесс парсинга.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
              <span className="text-sm font-medium">Статус</span>
              <ParserStatus status={state?.status || 'stopped'} />
            </div>

            {state?.status === 'running' && state.task ? (
              <div className="space-y-2">
                <p className="text-sm font-medium">
                  Обработка: {state.task.group_name}
                </p>
                <Progress value={state.task.progress} className="w-full" />
                <p className="text-xs text-slate-400">
                  {state.task.posts_processed} постов обработано
                </p>
              </div>
            ) : (
              <Select
                onValueChange={setSelectedGroupId}
                defaultValue={selectedGroupId}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Выберите группу" />
                </SelectTrigger>
                <SelectContent>
                  {groups.map((group) => (
                    <SelectItem key={group.id} value={String(group.id)}>
                      {group.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}

            {state?.status === 'running' ? (
              <Button
                className="w-full"
                variant="destructive"
                onClick={() => stopParserMutation.mutate()}
                disabled={isActionInProgress}
              >
                <Pause className="mr-2 h-4 w-4" />
                Остановить
              </Button>
            ) : (
              <Button
                className="w-full"
                onClick={handleStart}
                disabled={!selectedGroupId || isActionInProgress}
              >
                <Play className="mr-2 h-4 w-4" />
                Запустить
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Stats */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5" /> Статистика
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {isLoadingStats ? (
              <LoadingSpinner />
            ) : (
              <>
                <div className="flex justify-between">
                  <span className="text-slate-400">Всего запусков</span>
                  <span>{stats?.total_runs || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Успешных</span>
                  <span className="text-green-500">
                    {stats?.successful_runs || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Неуспешных</span>
                  <span className="text-red-500">{stats?.failed_runs || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Среднее время</span>
                  <span>
                    {Math.round(stats?.average_duration || 0)} сек
                  </span>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* History */}
      <div className="md:col-span-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5" /> История запусков
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoadingHistory ? (
              <div className="flex justify-center items-center h-64">
                <LoadingSpinner />
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Группа</TableHead>
                    <TableHead>Статус</TableHead>
                    <TableHead>Длительность</TableHead>
                    <TableHead>Время</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {history?.items?.map((task: ParseTaskResponse) => (
                    <TableRow key={task.task_id}>
                      <TableCell>{task.group_name}</TableCell>
                      <TableCell>
                        <ParserStatus status={task.status} />
                      </TableCell>
                      <TableCell>
                        {task.stats?.duration_seconds
                          ? `${Math.round(task.stats.duration_seconds)} сек`
                          : '-'}
                      </TableCell>
                      <TableCell>
                        {formatDistanceToNow(new Date(task.started_at), {
                          addSuffix: true,
                          locale: ru,
                        })}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
