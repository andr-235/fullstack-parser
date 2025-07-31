'use client'

import { useState } from 'react'
import { VKGroupMonitoring } from '@/types/api'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Button,
  LoadingSpinner,
  Badge,
  Progress,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/shared/ui'
import {
  useMonitoringStats,
  useActiveMonitoringGroups,
  useEnableGroupMonitoring,
  useSchedulerStatus,
  useStartScheduler,
  useStopScheduler,
} from '../hooks'
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
  Settings,
  TrendingUp,
  AlertCircle,
  Pause,
  RefreshCw,
  BarChart3,
  Filter,
  Search,
  Calendar,
  Timer,
  Shield,
  Wifi,
  WifiOff,
} from 'lucide-react'
import { formatDistanceToNow, format } from 'date-fns'
import { ru } from 'date-fns/locale'
import {
  formatDateTimeShort,
  isOverdue,
  calculateProgress,
  formatNextRunTime,
} from '@/shared/lib/time-utils'
import GroupsMonitoringTable from './GroupsMonitoringTable'
import { toast } from 'react-hot-toast'
import { useGroups } from '@/entities/group'
import MonitoringHistory from './MonitoringHistory'

export default function MonitoringPage() {
  const [activeTab, setActiveTab] = useState('overview')
  const [filterStatus, setFilterStatus] = useState<
    'all' | 'active' | 'error' | 'waiting'
  >('all')

  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
  } = useMonitoringStats()

  const {
    data: activeGroups,
    isLoading: activeGroupsLoading,
    error: activeGroupsError,
  } = useActiveMonitoringGroups()

  const { data: schedulerStatus, isLoading: schedulerLoading } =
    useSchedulerStatus()

  const { data: allGroups } = useGroups({ active_only: true })
  const enableMonitoringMutation = useEnableGroupMonitoring()
  const startSchedulerMutation = useStartScheduler()
  const stopSchedulerMutation = useStopScheduler()

  if (statsLoading || activeGroupsLoading || schedulerLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="flex flex-col items-center justify-center space-y-4">
          <LoadingSpinner className="h-8 w-8 text-blue-500" />
          <span className="text-slate-400 font-medium">
            Загрузка мониторинга...
          </span>
        </div>
      </div>
    )
  }

  if (statsError || activeGroupsError) {
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
              {statsError?.message || activeGroupsError?.message}
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Вычисляем статус системы
  const systemStatus = (() => {
    if (!schedulerStatus?.is_running) {
      return {
        status: 'Остановлен',
        color: 'text-red-400',
        icon: <Pause className="h-5 w-5" />,
        description: 'Планировщик не работает',
      }
    }

    if (!schedulerStatus?.redis_connected) {
      return {
        status: 'Ошибка Redis',
        color: 'text-red-400',
        icon: <WifiOff className="h-5 w-5" />,
        description: 'Нет подключения к Redis',
      }
    }

    if (stats?.monitored_groups && stats.monitored_groups > 0) {
      return {
        status: 'Работает',
        color: 'text-green-400',
        icon: <Wifi className="h-5 w-5" />,
        description: 'Мониторинг активен',
      }
    }

    return {
      status: 'Готов',
      color: 'text-yellow-400',
      icon: <Clock className="h-5 w-5" />,
      description: 'Ожидает настройки',
    }
  })()

  // Вычисляем время до следующего мониторинга
  const nextMonitoringTime = (() => {
    if (!stats?.next_monitoring_at || stats.next_monitoring_at === 'null') {
      return {
        text: 'Не запланировано',
        progress: 0,
        status: 'waiting',
      }
    }

    // Вычисляем прогресс (предполагаем интервал 5 минут)
    const progress = calculateProgress(stats.next_monitoring_at, 5)

    // Используем локальное время, которое уже приходит с сервера
    const displayText =
      stats.next_monitoring_at_local ||
      formatNextRunTime(stats.next_monitoring_at)

    return {
      text: displayText,
      progress,
      status: 'running',
    }
  })()

  // Фильтруем группы по статусу
  const filteredGroups =
    activeGroups?.items?.filter((group: VKGroupMonitoring) => {
      if (filterStatus === 'all') return true
      if (
        filterStatus === 'active' &&
        group.auto_monitoring_enabled &&
        !group.last_monitoring_error
      )
        return true
      if (filterStatus === 'error' && group.last_monitoring_error) return true
      if (
        filterStatus === 'waiting' &&
        group.auto_monitoring_enabled &&
        !group.last_monitoring_success
      )
        return true
      return false
    }) || []

  // Статистика по группам
  const groupsStats = {
    total: activeGroups?.items?.length || 0, // Группы с мониторингом
    allGroups: allGroups?.total || 0, // Общее количество всех групп
    active:
      activeGroups?.items?.filter(
        (g: VKGroupMonitoring) =>
          g.auto_monitoring_enabled && !g.last_monitoring_error
      ).length || 0,
    error:
      activeGroups?.items?.filter(
        (g: VKGroupMonitoring) => g.last_monitoring_error
      ).length || 0,
    waiting:
      activeGroups?.items?.filter(
        (g: VKGroupMonitoring) =>
          g.auto_monitoring_enabled && !g.last_monitoring_success
      ).length || 0,
  }

  const handleAddAllGroupsToMonitoring = () => {
    if (!allGroups?.items || allGroups.items.length === 0) {
      toast.error('Нет групп для добавления в мониторинг')
      return
    }

    const groupsToAdd = allGroups.items.filter(
      (group) => !activeGroups?.items.some((active) => active.id === group.id)
    )

    if (groupsToAdd.length === 0) {
      toast.success('Все группы уже добавлены в мониторинг')
      return
    }

    let addedCount = 0
    let errorCount = 0

    const addGroup = async (index: number) => {
      if (index >= groupsToAdd.length) {
        if (addedCount > 0) {
          toast.success(`Добавлено ${addedCount} групп в мониторинг! ✅`)
        }
        if (errorCount > 0) {
          toast.error(`Ошибка при добавлении ${errorCount} групп`)
        }
        return
      }

      const group = groupsToAdd[index]
      try {
        await enableMonitoringMutation.mutateAsync({
          groupId: group.id,
          intervalMinutes: 60,
          priority: 5,
        })
        addedCount++
      } catch (error) {
        errorCount++
        console.error(`Ошибка добавления группы ${group.name}:`, error)
      }

      setTimeout(() => addGroup(index + 1), 100)
    }

    const loadingToast = toast.loading(
      `Добавление ${groupsToAdd.length} групп в мониторинг...`
    )
    addGroup(0)
  }

  const handleSchedulerToggle = () => {
    if (schedulerStatus?.is_running) {
      stopSchedulerMutation.mutate()
    } else {
      startSchedulerMutation.mutate(300) // 5 минут по умолчанию
    }
  }

  return (
    <div className="space-y-6">
      {/* Заголовок с улучшенным статусом */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-white/10 rounded-lg">
              <Activity className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Мониторинг групп</h1>
              <p className="text-slate-300">
                Автоматический мониторинг VK групп на новые комментарии
              </p>
            </div>
          </div>

          {/* Статус системы */}
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className={`flex items-center gap-2 ${systemStatus.color}`}>
                {systemStatus.icon}
                <span className="font-medium">{systemStatus.status}</span>
              </div>
              <p className="text-sm text-slate-400">
                {systemStatus.description}
              </p>
            </div>

            <div className="flex items-center space-x-3">
              <Button
                onClick={handleAddAllGroupsToMonitoring}
                disabled={enableMonitoringMutation.isPending}
                className="bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:scale-105"
              >
                {enableMonitoringMutation.isPending ? (
                  <LoadingSpinner className="h-4 w-4 mr-2" />
                ) : (
                  <Plus className="h-4 w-4 mr-2" />
                )}
                Добавить все группы
              </Button>
              <Button
                onClick={handleSchedulerToggle}
                disabled={
                  startSchedulerMutation.isPending ||
                  stopSchedulerMutation.isPending
                }
                className={`transition-all duration-200 hover:scale-105 ${
                  schedulerStatus?.is_running
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : 'bg-green-600 hover:bg-green-700 text-white'
                }`}
              >
                {startSchedulerMutation.isPending ||
                stopSchedulerMutation.isPending ? (
                  <LoadingSpinner className="h-4 w-4 mr-2" />
                ) : schedulerStatus?.is_running ? (
                  <Pause className="h-4 w-4 mr-2" />
                ) : (
                  <Play className="h-4 w-4 mr-2" />
                )}
                {schedulerStatus?.is_running ? 'Остановить' : 'Запустить цикл'}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Основные метрики с улучшенным дизайном */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <Users className="h-5 w-5 text-blue-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">
                  Всего групп
                </p>
                <p className="text-2xl font-bold text-blue-400">
                  {allGroups?.total || 0}
                </p>
                <p className="text-xs text-slate-400">Активные группы</p>
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
                <p className="text-xs text-slate-400">
                  {stats?.ready_for_monitoring || 0} готовы
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <Timer className="h-5 w-5 text-purple-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">
                  Следующий запуск
                </p>
                <p
                  className={`text-sm font-medium ${
                    nextMonitoringTime.status === 'overdue'
                      ? 'text-red-400'
                      : nextMonitoringTime.status === 'waiting'
                        ? 'text-slate-400'
                        : 'text-purple-400'
                  }`}
                >
                  {nextMonitoringTime.text}
                </p>
                {nextMonitoringTime.status === 'running' && (
                  <Progress
                    value={nextMonitoringTime.progress}
                    className="mt-2 h-1"
                  />
                )}
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
                <p className="text-sm font-medium text-slate-300">
                  Статус системы
                </p>
                <div className={`text-sm font-medium ${systemStatus.color}`}>
                  {systemStatus.status}
                </div>
                <p className="text-xs text-slate-400">
                  {schedulerStatus?.is_running
                    ? 'Планировщик активен'
                    : 'Планировщик остановлен'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Вкладки с детальной информацией */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="space-y-4"
      >
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Обзор
          </TabsTrigger>
          <TabsTrigger value="groups" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Группы ({groupsStats.total})
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Настройки
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* Статистика по группам */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="border-slate-700 bg-slate-800">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400">Активные</p>
                    <p className="text-2xl font-bold text-green-400">
                      {groupsStats.active}
                    </p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-slate-700 bg-slate-800">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400">Ожидают</p>
                    <p className="text-2xl font-bold text-yellow-400">
                      {groupsStats.waiting}
                    </p>
                  </div>
                  <Clock className="h-8 w-8 text-yellow-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-slate-700 bg-slate-800">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400">Ошибки</p>
                    <p className="text-2xl font-bold text-red-400">
                      {groupsStats.error}
                    </p>
                  </div>
                  <AlertCircle className="h-8 w-8 text-red-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-slate-700 bg-slate-800">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400">Всего</p>
                    <p className="text-2xl font-bold text-blue-400">
                      {groupsStats.allGroups}
                    </p>
                    <p className="text-xs text-slate-400">
                      {groupsStats.total} с мониторингом
                    </p>
                  </div>
                  <Target className="h-8 w-8 text-blue-400" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Информация о планировщике */}
          <Card className="border-slate-700 bg-slate-800">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-slate-200 flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-400" />
                Статус планировщика
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center space-x-3">
                  <div
                    className={`p-2 rounded-lg ${schedulerStatus?.is_running ? 'bg-green-600' : 'bg-red-600'}`}
                  >
                    {schedulerStatus?.is_running ? (
                      <Play className="h-4 w-4 text-white" />
                    ) : (
                      <Pause className="h-4 w-4 text-white" />
                    )}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-300">
                      Планировщик
                    </p>
                    <p
                      className={`text-sm ${schedulerStatus?.is_running ? 'text-green-400' : 'text-red-400'}`}
                    >
                      {schedulerStatus?.is_running ? 'Работает' : 'Остановлен'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div
                    className={`p-2 rounded-lg ${schedulerStatus?.redis_connected ? 'bg-green-600' : 'bg-red-600'}`}
                  >
                    {schedulerStatus?.redis_connected ? (
                      <Wifi className="h-4 w-4 text-white" />
                    ) : (
                      <WifiOff className="h-4 w-4 text-white" />
                    )}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-300">Redis</p>
                    <p
                      className={`text-sm ${schedulerStatus?.redis_connected ? 'text-green-400' : 'text-red-400'}`}
                    >
                      {schedulerStatus?.redis_connected
                        ? 'Подключен'
                        : 'Отключен'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-blue-600 rounded-lg">
                    <Timer className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-300">
                      Интервал
                    </p>
                    <p className="text-sm text-blue-400">
                      {schedulerStatus?.monitoring_interval_seconds
                        ? `${Math.round(schedulerStatus.monitoring_interval_seconds / 60)} мин`
                        : 'Не настроен'}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* История мониторинга */}
          <Card className="border-slate-700 bg-slate-800">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-slate-200 flex items-center gap-2">
                <RefreshCw className="h-5 w-5 text-purple-400" />
                История мониторинга
              </CardTitle>
            </CardHeader>
            <CardContent>
              <MonitoringHistory />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="groups" className="space-y-4">
          {/* Фильтры для групп */}
          <Card className="border-slate-700 bg-slate-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <Filter className="h-4 w-4 text-slate-400" />
                    <span className="text-sm text-slate-400">Фильтр:</span>
                  </div>
                  <div className="flex space-x-2">
                    {[
                      { key: 'all', label: 'Все', count: groupsStats.total },
                      {
                        key: 'active',
                        label: 'Активные',
                        count: groupsStats.active,
                      },
                      {
                        key: 'waiting',
                        label: 'Ожидают',
                        count: groupsStats.waiting,
                      },
                      {
                        key: 'error',
                        label: 'Ошибки',
                        count: groupsStats.error,
                      },
                    ].map((filter) => (
                      <Button
                        key={filter.key}
                        variant={
                          filterStatus === filter.key ? 'default' : 'outline'
                        }
                        size="sm"
                        onClick={() => setFilterStatus(filter.key as any)}
                        className="text-xs"
                      >
                        {filter.label} ({filter.count})
                      </Button>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Таблица групп */}
          <Card className="border-slate-700 bg-slate-800 shadow-lg">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-slate-200 flex items-center gap-2">
                <Activity className="h-5 w-5 text-green-400" />
                Группы с мониторингом
                <span className="text-sm text-slate-400 font-normal">
                  ({filteredGroups.length} из {groupsStats.total} мониторинг,{' '}
                  {groupsStats.allGroups} всего)
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <GroupsMonitoringTable groups={filteredGroups} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card className="border-slate-700 bg-slate-800">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-slate-200 flex items-center gap-2">
                <Settings className="h-5 w-5 text-blue-400" />
                Настройки мониторинга
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-300">
                Настройки мониторинга будут добавлены в следующем обновлении.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
