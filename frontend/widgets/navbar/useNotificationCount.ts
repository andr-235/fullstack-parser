import { useState, useEffect, useCallback } from 'react'

import { httpClient } from '@/shared/lib'

interface DashboardStatsResponse {
  today_comments: number
}

interface NotificationState {
  count: number
  loading: boolean
  error: string | null
}

/**
 * Хук для получения количества уведомлений.
 * Выполняет запросы к API для получения глобальной статистики и статистики дашборда,
 * суммирует количество комментариев за сегодня и возвращает общее количество уведомлений.
 * Автоматически обновляет данные каждые 30 секунд.
 *
 * @returns {number} Текущее количество уведомлений
 */
export function useNotificationCount() {
  const [state, setState] = useState<NotificationState>({
    count: 0,
    loading: true,
    error: null,
  })

  /**
   * Асинхронная функция для получения количества уведомлений с сервера.
   * Выполняет параллельные запросы к API глобальной статистики и статистики дашборда,
   * суммирует количество комментариев за сегодня из успешных ответов.
   * В случае ошибки логирует её и обновляет состояние с сообщением об ошибке.
   *
   * @async
   * @returns {Promise<void>} Не возвращает значение, обновляет внутреннее состояние
   */
  const fetchNotificationCount = useCallback(async (): Promise<void> => {
    setState(prev => ({ ...prev, loading: true, error: null }))

    try {
      const [globalStats, dashboardStats] = await Promise.allSettled([
        httpClient.get('/api/stats/global'),
        httpClient.get<DashboardStatsResponse>('/api/stats/dashboard'),
      ])

      let notificationCount: number = 0

      // Обрабатываем успешные ответы
      if (dashboardStats.status === 'fulfilled' && dashboardStats.value?.today_comments) {
        notificationCount += dashboardStats.value.today_comments
      }

      // Можно добавить другие типы уведомлений
      // if (globalStats.status === 'fulfilled' && hasErrors) notificationCount += 1

      setState({
        count: notificationCount,
        loading: false,
        error: null,
      })
    } catch (error) {
      console.error('Failed to fetch notification count:', error)
      setState({
        count: 0,
        loading: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      })
    }
  }, [])

  useEffect(() => {
    fetchNotificationCount()

    // Автообновление каждые 30 секунд
    const interval = setInterval(fetchNotificationCount, 30000)
    return () => clearInterval(interval)
  }, [fetchNotificationCount])

  return state.count
}
