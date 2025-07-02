"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { BarChart3, Users, MessageSquare, KeyRound } from "lucide-react"
import { api } from "@/lib/api"
import type { GlobalStats } from "@/types/api"

export default function DashboardPage() {
  const [stats, setStats] = useState<GlobalStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setError(null)
        const data = await api.getGlobalStats()
        setStats(data)
      } catch (error) {
        console.error("Error fetching stats:", error)
        setError(error instanceof Error ? error.message : "Ошибка загрузки данных")
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="text-red-500 text-center">
          <h3 className="text-lg font-semibold mb-2">Ошибка подключения</h3>
          <p className="text-sm">{error}</p>
          <p className="text-xs mt-2 text-gray-500">
            Убедитесь что backend запущен на localhost:8000
          </p>
        </div>
        <button 
          onClick={() => window.location.reload()} 
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          Попробовать снова
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Дашборд</h1>
        <p className="text-gray-600">Обзор системы VK Comments Parser</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Всего комментариев</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.total_comments?.toLocaleString('ru-RU') || 0}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-blue-100">
              <MessageSquare className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Активные группы</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.active_groups?.toLocaleString('ru-RU') || 0}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-green-100">
              <Users className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Ключевых слов</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.total_keywords?.toLocaleString('ru-RU') || 0}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-purple-100">
              <KeyRound className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Всего групп</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.total_groups?.toLocaleString('ru-RU') || 0}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-orange-100">
              <BarChart3 className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* Дополнительная статистика */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Качество парсинга</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Комментарии с ключевыми словами</span>
              <span className="text-sm font-medium">
                {stats?.comments_with_keywords?.toLocaleString('ru-RU') || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Процент покрытия</span>
              <span className="text-sm font-medium">
                {stats?.total_comments && stats?.total_comments > 0 
                  ? Math.round((stats.comments_with_keywords / stats.total_comments) * 100) 
                  : 0}%
              </span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Статус системы</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Backend API</span>
              <span className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium text-green-600">Активен</span>
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">База данных</span>
              <span className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium text-green-600">Подключена</span>
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Отладочная информация (только в development) */}
      {process.env.NODE_ENV === 'development' && stats && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Отладочная информация</h3>
          <pre className="text-sm bg-gray-100 p-4 rounded overflow-auto max-h-64">
            {JSON.stringify(stats, null, 2)}
          </pre>
        </Card>
      )}
    </div>
  )
}
