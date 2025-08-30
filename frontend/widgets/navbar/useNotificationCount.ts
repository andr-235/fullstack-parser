import { useState, useEffect } from 'react'
import { apiClient } from '@/shared/lib/index'

export function useNotificationCount() {
  const [count, setCount] = useState(0)

  useEffect(() => {
    const fetchNotificationCount = async () => {
      try {
        // Получаем статистику для определения количества уведомлений
        const [globalStats, dashboardStats] = await Promise.all([
          apiClient.getGlobalStats().catch(() => null),
          apiClient.getDashboardStats().catch(() => null),
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

    // Обновляем каждые 30 секунд
    const interval = setInterval(fetchNotificationCount, 30000)

    return () => clearInterval(interval)
  }, [])

  return count
}
