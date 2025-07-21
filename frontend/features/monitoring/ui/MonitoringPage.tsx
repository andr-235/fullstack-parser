'use client'

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Button,
  LoadingSpinner,
} from '@/shared/ui'
import {
  useMonitoringStats,
  useAvailableGroupsForMonitoring,
  useActiveMonitoringGroups,
  useRunMonitoringCycle,
} from '@/hooks/use-monitoring'
import {
  Activity,
  Play,
  Users,
  Clock,
  AlertTriangle,
  CheckCircle,
  Plus,
  Eye,
  Target,
  Zap,
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import GroupsMonitoringTable from './GroupsMonitoringTable'
import AvailableGroupsTable from './AvailableGroupsTable'

export default function MonitoringPage() {
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
  } = useMonitoringStats()
  const {
    data: availableGroups,
    isLoading: availableGroupsLoading,
    error: availableGroupsError,
  } = useAvailableGroupsForMonitoring()
  const {
    data: activeGroups,
    isLoading: activeGroupsLoading,
    error: activeGroupsError,
  } = useActiveMonitoringGroups()
  const runCycleMutation = useRunMonitoringCycle()

  if (statsLoading || availableGroupsLoading || activeGroupsLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="flex flex-col items-center justify-center space-y-4">
          <LoadingSpinner className="h-8 w-8 text-blue-500" />
          <span className="text-slate-400 font-medium">Загрузка мониторинга...</span>
        </div>
      </div>
    )
  }

  if (statsError || availableGroupsError || activeGroupsError) {
    return (
      <div className="flex justify-center items-center h-full">
        <Card className="w-96 border-slate-700 bg-slate-800">
          <CardHeader>
            <CardTitle className="text-red-400 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Ошибка
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-300">
              Не удалось загрузить данные мониторинга. Попробуйте обновить
              страницу.
            </p>
            <p className="text-sm text-slate-400 mt-2">
              {statsError?.message ||
                availableGroupsError?.message ||
                activeGroupsError?.message}
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const nextMonitoringTime = (() => {
    if (!stats?.next_monitoring_at || stats.next_monitoring_at === 'null') {
      return 'Не запланировано'
    }

    const nextTime = new Date(stats.next_monitoring_at)
    const now = new Date()

    // Если время в прошлом, показываем "Просрочено"
    if (nextTime < now) {
      return 'Просрочено'
    }

    return formatDistanceToNow(nextTime, {
      addSuffix: true,
      locale: ru,
    })
  })()

  const systemStatus = (() => {
    if (!stats) return { status: 'Неизвестно', color: 'text-slate-400', icon: '❓' }

    if (stats.ready_for_monitoring > 0) {
      return {
        status: `${stats.ready_for_monitoring} групп ждут проверки`,
        color: 'text-yellow-400',
        icon: '⚠️'
      }
    }

    if (stats.monitored_groups > 0) {
      return {
        status: 'Система работает',
        color: 'text-green-400',
        icon: '✅'
      }
    }

    return {
      status: 'Мониторинг не настроен',
      color: 'text-slate-400',
      icon: '⏸️'
    }
  })()

  const monitoringStatus = (() => {
    if (!stats) return { status: 'Неизвестно', color: 'text-slate-400' }

    if (stats.monitored_groups === 0) {
      return { status: 'Не настроен', color: 'text-slate-400' }
    }

    if (stats.ready_for_monitoring > 0) {
      return { status: `${stats.ready_for_monitoring} готовы`, color: 'text-yellow-400' }
    }

    return { status: 'Все обработаны', color: 'text-green-400' }
  })()

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3 mb-2">
            <div className="p-2 bg-white/10 rounded-lg">
              <Eye className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Мониторинг групп ВК</h1>
              <p className="text-slate-300 mt-1">
                Автоматический мониторинг и парсинг групп ВКонтакте
              </p>
            </div>
          </div>
          <Button
            onClick={() => runCycleMutation.mutate()}
            disabled={runCycleMutation.isPending}
            className="bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:scale-105"
          >
            <Play className="h-4 w-4 mr-2" />
            {runCycleMutation.isPending ? 'Запуск...' : 'Запустить цикл'}
          </Button>
        </div>
      </div>

      {/* Карточки статистики */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <Users className="h-5 w-5 text-blue-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Всего групп</p>
                <p className="text-2xl font-bold text-blue-400">{stats?.total_groups || 0}</p>
                <p className="text-xs text-slate-400">
                  {stats?.active_groups || 0} активных
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <Activity className="h-5 w-5 text-green-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Мониторинг</p>
                <p className="text-2xl font-bold text-green-400">
                  {stats?.monitored_groups || 0}
                </p>
                <p className={`text-xs ${monitoringStatus.color}`}>
                  {monitoringStatus.status}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <Clock className="h-5 w-5 text-purple-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Следующий запуск</p>
                <div className={`text-sm font-medium ${nextMonitoringTime === 'Просрочено' ? 'text-red-400' :
                  nextMonitoringTime === 'Не запланировано' ? 'text-slate-400' :
                    'text-slate-200'
                  }`}>
                  {nextMonitoringTime}
                </div>
                <p className="text-xs text-slate-400">Автоматический цикл</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <span className="text-lg">{systemStatus.icon}</span>
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Статус системы</p>
                <div className={`text-sm font-medium ${systemStatus.color}`}>
                  {systemStatus.status}
                </div>
                <p className="text-xs text-slate-400">
                  {stats?.monitored_groups && stats.monitored_groups > 0 ? 'Мониторинг активен' : 'Мониторинг не настроен'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Группы с активным мониторингом */}
      <Card className="border-slate-700 bg-slate-800 shadow-lg">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-slate-200 flex items-center gap-2">
            <Activity className="h-5 w-5 text-green-400" />
            Группы с активным мониторингом
          </CardTitle>
        </CardHeader>
        <CardContent>
          <GroupsMonitoringTable groups={activeGroups?.items || []} />
        </CardContent>
      </Card>

      {/* Группы, доступные для мониторинга */}
      <Card className="border-slate-700 bg-slate-800 shadow-lg">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-slate-200 flex items-center gap-2">
            <Plus className="h-5 w-5 text-blue-400" />
            Группы, доступные для мониторинга
          </CardTitle>
        </CardHeader>
        <CardContent>
          <AvailableGroupsTable groups={availableGroups?.items || []} />
        </CardContent>
      </Card>
    </div>
  )
}
