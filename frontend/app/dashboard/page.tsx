'use client'

import { Card } from '@/components/ui/card'
import { useStats } from '@/hooks/use-stats'
import { Users, MessageSquare, KeyRound } from 'lucide-react'

export default function DashboardPage() {
  const { data: stats, isLoading, error } = useStats()

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    )
  }

  if (error) {
    return (
      <div role="alert" className="alert alert-error">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="stroke-current shrink-0 h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <span>Ошибка при загрузке статистики: {error.message}</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="stat bg-base-100 rounded-box shadow">
          <div className="stat-figure text-primary">
            <Users size={32} />
          </div>
          <div className="stat-title">Группы</div>
          <div className="stat-value">{stats?.groups_count || 0}</div>
          <div className="stat-desc">Отслеживаемых групп</div>
        </div>

        <div className="stat bg-base-100 rounded-box shadow">
          <div className="stat-figure text-primary">
            <MessageSquare size={32} />
          </div>
          <div className="stat-title">Комментарии</div>
          <div className="stat-value">{stats?.comments_count || 0}</div>
          <div className="stat-desc">Всего комментариев</div>
        </div>

        <div className="stat bg-base-100 rounded-box shadow">
          <div className="stat-figure text-primary">
            <KeyRound size={32} />
          </div>
          <div className="stat-title">Ключевые слова</div>
          <div className="stat-value">{stats?.keywords_count || 0}</div>
          <div className="stat-desc">Отслеживаемых слов</div>
        </div>
      </div>

      {/* Placeholder for future charts */}
      <div className="card bg-base-100 shadow">
        <div className="card-body">
          <h2 className="card-title">Активность комментариев</h2>
          <div className="h-64 flex justify-center items-center text-gray-400">
            {/* Chart will be here */}
            (График в разработке)
          </div>
        </div>
      </div>
    </div>
  )
}
