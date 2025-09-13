import { useState, useEffect } from 'react'

import { httpClient } from '@/shared/lib'

interface DashboardStatsResponse {
  today_comments: number
}

export function useNotificationCount() {
  const [count, setCount] = useState(0)

  useEffect(() => {
    const fetchNotificationCount = async () => {
      try {
        // Получаем статистику для определения количества уведомлений
        const [globalStats, dashboardStats] = await Promise.all([
          httpClient.get('/api/stats/global').catch(() => null),
          httpClient.get<DashboardStatsResponse>('/api/stats/dashboard').catch(() => null),
        ])

        let notificationCount = 0

        // Считаем новые комментарии как уведомления
        if (dashboardStats?.today_comments) {
          notificationCount += dashboardStats.today_comments
        }

        // Можно добавить другие типы уведомлений
        // if (hasErrors) notificationCount += 1
        // if (hasNewGroups) notificationCount += 1

        setCount(notificationCount)
      } catch (error) {
        console.error('Failed to fetch notification count:', error)
        setCount(0)
      }
    }

    fetchNotificationCount()

    // Автообновление отключено для снижения нагрузки
    // const interval = setInterval(fetchNotificationCount, 30000)
    // return () => clearInterval(interval)
  }, [])

  return count
}
