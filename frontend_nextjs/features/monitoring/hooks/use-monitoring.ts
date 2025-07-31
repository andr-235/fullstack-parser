import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, createQueryKey } from '@/shared/lib/api'
import type {
  MonitoringStats,
  VKGroupMonitoring,
  MonitoringGroupUpdate,
  MonitoringRunResult,
  SchedulerStatus,
} from '@/types/api'
import toast from 'react-hot-toast'

/**
 * Хук для получения статистики мониторинга
 */
export function useMonitoringStats() {
  return useQuery<MonitoringStats>({
    queryKey: createQueryKey.monitoringStats(),
    queryFn: () => api.getMonitoringStats(),
    staleTime: 30 * 1000, // 30 секунд
    refetchInterval: 60 * 1000, // Обновляем каждую минуту
  })
}

/**
 * Хук для получения статуса планировщика
 */
export function useSchedulerStatus() {
  return useQuery<SchedulerStatus>({
    queryKey: createQueryKey.schedulerStatus(),
    queryFn: () => api.getSchedulerStatus(),
    staleTime: 10 * 1000, // 10 секунд - частое обновление
    refetchInterval: 30 * 1000, // Обновляем каждые 30 секунд
  })
}

/**
 * Хук для получения групп с мониторингом
 */
export function useMonitoringGroups(params?: {
  active_only?: boolean
  monitoring_enabled?: boolean
}) {
  return useQuery({
    queryKey: createQueryKey.monitoringGroups(params),
    queryFn: () => api.getMonitoringGroups(params),
    staleTime: 60 * 1000, // 1 минута
  })
}

/**
 * Хук для получения групп, доступных для мониторинга
 */
export function useAvailableGroupsForMonitoring() {
  return useQuery({
    queryKey: createQueryKey.availableGroupsForMonitoring(),
    queryFn: () => api.getAvailableGroupsForMonitoring(),
    staleTime: 60 * 1000, // 1 минута
  })
}

/**
 * Хук для получения групп с активным мониторингом
 */
export function useActiveMonitoringGroups() {
  return useQuery({
    queryKey: createQueryKey.activeMonitoringGroups(),
    queryFn: () => api.getActiveMonitoringGroups(),
    staleTime: 30 * 1000, // 30 секунд - более частое обновление
    refetchInterval: 60 * 1000, // Обновляем каждую минуту
  })
}

/**
 * Хук для включения мониторинга группы
 */
export function useEnableGroupMonitoring() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      groupId,
      intervalMinutes,
      priority,
    }: {
      groupId: number
      intervalMinutes: number
      priority: number
    }) => api.enableGroupMonitoring(groupId, intervalMinutes, priority),
    onSuccess: () => {
      toast.success('Мониторинг группы включен')
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringStats(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringGroups(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.availableGroupsForMonitoring(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.activeMonitoringGroups(),
      })
    },
    onError: (error) => {
      toast.error(`Ошибка включения мониторинга: ${error.message}`)
    },
  })
}

/**
 * Хук для отключения мониторинга группы
 */
export function useDisableGroupMonitoring() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (groupId: number) => api.disableGroupMonitoring(groupId),
    onSuccess: () => {
      toast.success('Мониторинг группы отключен')
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringStats(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringGroups(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.availableGroupsForMonitoring(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.activeMonitoringGroups(),
      })
    },
    onError: (error) => {
      toast.error(`Ошибка отключения мониторинга: ${error.message}`)
    },
  })
}

/**
 * Хук для обновления настроек мониторинга группы
 */
export function useUpdateGroupMonitoring() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      groupId,
      updateData,
    }: {
      groupId: number
      updateData: MonitoringGroupUpdate
    }) => api.updateGroupMonitoring(groupId, updateData),
    onSuccess: () => {
      toast.success('Настройки мониторинга обновлены')
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringStats(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringGroups(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.availableGroupsForMonitoring(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.activeMonitoringGroups(),
      })
    },
    onError: (error) => {
      toast.error(`Ошибка обновления настроек: ${error.message}`)
    },
  })
}

/**
 * Хук для запуска мониторинга группы вручную
 */
export function useRunGroupMonitoring() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (groupId: number) => api.runGroupMonitoring(groupId),
    onSuccess: () => {
      toast.success('Мониторинг группы запущен')
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringStats(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringGroups(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.availableGroupsForMonitoring(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.activeMonitoringGroups(),
      })
    },
    onError: (error) => {
      toast.error(`Ошибка запуска мониторинга: ${error.message}`)
    },
  })
}

/**
 * Хук для запуска цикла мониторинга всех групп
 */
export function useRunMonitoringCycle() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => api.runMonitoringCycle(),
    onSuccess: (data: MonitoringRunResult) => {
      toast.success(
        `Цикл мониторинга завершён. Обработано групп: ${data.monitored_groups}, успешно: ${data.successful_runs}, ошибок: ${data.failed_runs}`
      )
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringStats(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringGroups(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.availableGroupsForMonitoring(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.activeMonitoringGroups(),
      })
    },
    onError: (error) => {
      toast.error(`Ошибка запуска цикла мониторинга: ${error.message}`)
    },
  })
}

/**
 * Хук для запуска планировщика мониторинга
 */
export function useStartScheduler() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (intervalSeconds: number = 300) =>
      api.startScheduler(intervalSeconds),
    onSuccess: () => {
      toast.success('Планировщик мониторинга запущен')
      queryClient.invalidateQueries({
        queryKey: createQueryKey.schedulerStatus(),
      })
    },
    onError: (error) => {
      toast.error(`Ошибка запуска планировщика: ${error.message}`)
    },
  })
}

/**
 * Хук для остановки планировщика мониторинга
 */
export function useStopScheduler() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => api.stopScheduler(),
    onSuccess: () => {
      toast.success('Планировщик мониторинга остановлен')
      queryClient.invalidateQueries({
        queryKey: createQueryKey.schedulerStatus(),
      })
    },
    onError: (error) => {
      toast.error(`Ошибка остановки планировщика: ${error.message}`)
    },
  })
}
