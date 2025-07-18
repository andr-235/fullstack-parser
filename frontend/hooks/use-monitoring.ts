import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, createQueryKey } from '@/lib/api'
import type {
  MonitoringStats,
  VKGroupMonitoring,
  MonitoringGroupUpdate,
  MonitoringRunResult,
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
 * Хук для получения групп с мониторингом
 */
export function useMonitoringGroups(params?: {
  active_only?: boolean
  monitoring_enabled?: boolean
  skip?: number
  limit?: number
}) {
  return useQuery({
    queryKey: createQueryKey.monitoringGroups(params),
    queryFn: () => api.getMonitoringGroups(params),
    staleTime: 60 * 1000, // 1 минута
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
      // Инвалидируем кеш
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringStats(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringGroups(),
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
      // Инвалидируем кеш
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringStats(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringGroups(),
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
      // Инвалидируем кеш
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringStats(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringGroups(),
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
      // Инвалидируем кеш через небольшую задержку
      setTimeout(() => {
        queryClient.invalidateQueries({
          queryKey: createQueryKey.monitoringGroups(),
        })
      }, 2000)
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
      // Инвалидируем кеш
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringStats(),
      })
      queryClient.invalidateQueries({
        queryKey: createQueryKey.monitoringGroups(),
      })
    },
    onError: (error) => {
      toast.error(`Ошибка запуска цикла мониторинга: ${error.message}`)
    },
  })
}
