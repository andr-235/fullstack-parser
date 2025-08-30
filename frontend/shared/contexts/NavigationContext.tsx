'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { apiClient } from '@/shared/lib'

interface NavigationStats {
 comments: {
  total: number
  new: number
 }
 groups: {
  total: number
  active: number
 }
 keywords: {
  total: number
  active: number
 }
}

interface NavigationContextType {
 stats: NavigationStats | null
 isLoading: boolean
 activePath: string
 refreshStats: () => Promise<void>
}

const NavigationContext = createContext<NavigationContextType | undefined>(undefined)

export function NavigationProvider({ children }: { children: React.ReactNode }) {
 const [stats, setStats] = useState<NavigationStats | null>(null)
 const [isLoading, setIsLoading] = useState(false)
 const pathname = usePathname()

 const fetchStats = async () => {
  try {
   setIsLoading(true)

   // Получаем данные параллельно для лучшей производительности
   const [globalStats, dashboardStats, commentsResponse] = await Promise.all([
    apiClient.getGlobalStats().catch(() => null),
    apiClient.getDashboardStats().catch(() => null),
    apiClient.getComments({ size: 1 }).catch(() => null),
   ])

   if (globalStats && dashboardStats) {
    setStats({
     comments: {
      total: globalStats.total_comments || 0,
      new: dashboardStats.today_comments || 0,
     },
     groups: {
      total: globalStats.total_groups || 0,
      active: globalStats.active_groups || 0,
     },
     keywords: {
      total: globalStats.total_keywords || 0,
      active: globalStats.active_keywords || 0,
     },
    })
   }
  } catch (error) {
   console.error('Failed to fetch navigation stats:', error)
  } finally {
   setIsLoading(false)
  }
 }

 useEffect(() => {
  fetchStats()

  // Обновляем статистику каждые 2 минуты
  const interval = setInterval(fetchStats, 2 * 60 * 1000)

  return () => clearInterval(interval)
 }, [])

 const refreshStats = async () => {
  await fetchStats()
 }

 return (
  <NavigationContext.Provider
   value={{
    stats,
    isLoading,
    activePath: pathname,
    refreshStats,
   }}
  >
   {children}
  </NavigationContext.Provider>
 )
}

export function useNavigation() {
 const context = useContext(NavigationContext)
 if (context === undefined) {
  throw new Error('useNavigation must be used within a NavigationProvider')
 }
 return context
}
