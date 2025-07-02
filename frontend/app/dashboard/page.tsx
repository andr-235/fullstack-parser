"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { BarChart3, Users, MessageSquare, KeyRound } from "lucide-react"

export default function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/v1/stats/global")
        const data = await response.json()
        setStats(data)
      } catch (error) {
        console.error("Error fetching stats:", error)
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
                {stats?.total_comments || 0}
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
                {stats?.active_groups || 0}
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
                {stats?.total_keywords || 0}
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
                {stats?.total_groups || 0}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-orange-100">
              <BarChart3 className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </Card>
      </div>

      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Данные статистики</h3>
        <pre className="text-sm bg-gray-100 p-4 rounded overflow-auto">
          {JSON.stringify(stats, null, 2)}
        </pre>
      </Card>
    </div>
  )
}
