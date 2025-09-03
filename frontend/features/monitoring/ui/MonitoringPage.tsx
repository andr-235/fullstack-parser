'use client'

import { useState } from 'react'

import { RefreshCw } from 'lucide-react'
import { Monitor, Activity, Server, AlertTriangle, CheckCircle } from 'lucide-react'

import { Button } from '@/shared/ui'
import { Alert, AlertDescription } from '@/shared/ui'

import { MonitoringCard } from './MonitoringCard'
import { MonitoringFilters } from './MonitoringFilters'
import { MonitoringList } from './MonitoringList'
import { MonitoringResources } from './MonitoringResources'
import { MonitoringServices } from './MonitoringServices'


export function MonitoringPage() {
 const [isRefreshing, setIsRefreshing] = useState(false)
 const [error, setError] = useState<string | null>(null)
 const [filters, setFilters] = useState<{ types?: string[] }>({})

 const handleRefresh = async () => {
  setIsRefreshing(true)
  setError(null)
  try {
   // Simulate API call
   await new Promise(resolve => setTimeout(resolve, 1000))
  } catch (err) {
   setError('Не удалось обновить данные мониторинга')
   console.error('Failed to refresh monitoring data:', err)
  } finally {
   setIsRefreshing(false)
  }
 }

 // Mock data - in real app this would come from API
 const statusCards = [
  {
   title: 'Статус системы',
   icon: Monitor,
   value: undefined,
   description: 'Работоспособен',
   status: 'success' as const,
   indicator: 'static' as const,
  },
  {
   title: 'Активные группы',
   icon: Server,
   value: 12,
   description: 'из 15 групп всего',
   status: 'info' as const,
  },
  {
   title: 'Статус парсера',
   icon: Activity,
   value: undefined,
   description: 'Работает',
   status: 'success' as const,
   indicator: 'pulse' as const,
  },
  {
   title: 'Предупреждения',
   icon: AlertTriangle,
   value: 3,
   description: 'требуют внимания',
   status: 'warning' as const,
  },
 ]

 const mockEvents = [
  {
   id: '1',
   type: 'success' as const,
   message: 'Парсер успешно запущен',
   timestamp: '2 минуты назад',
  },
  {
   id: '2',
   type: 'warning' as const,
   message: 'Обнаружено высокое использование памяти',
   timestamp: '5 минут назад',
  },
  {
   id: '3',
   type: 'success' as const,
   message: 'Подключение к базе данных восстановлено',
   timestamp: '10 минут назад',
  },
 ]

 return (
  <div className="container mx-auto py-6 space-y-6">
   {/* Header */}
   <div className="flex items-center justify-between">
    <div>
     <h1 className="text-3xl font-bold tracking-tight">Мониторинг</h1>
     <p className="text-muted-foreground">
      Мониторинг системы и проверка работоспособности
     </p>
    </div>

    <Button
     variant="outline"
     onClick={handleRefresh}
     disabled={isRefreshing}
    >
     <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
     Обновить
    </Button>
   </div>

   {/* Error State */}
   {error && (
    <Alert className="border-destructive">
     <AlertTriangle className="h-4 w-4" />
     <AlertDescription>
      {error}
      <Button
       variant="outline"
       size="sm"
       onClick={handleRefresh}
       className="ml-4"
      >
       Попробовать снова
      </Button>
     </AlertDescription>
    </Alert>
   )}

   {/* Filters */}
   <MonitoringFilters
    filters={filters}
    onFiltersChange={setFilters}
   />

   {/* Status Overview */}
   <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
    {statusCards.map((card, index) => (
     <MonitoringCard
      key={index}
      title={card.title}
      icon={card.icon}
      {...(card.value !== undefined && { value: card.value })}
      description={card.description}
      status={card.status}
      {...(card.indicator && { indicator: card.indicator })}
     />
    ))}
   </div>

   {/* Recent Activity */}
   <MonitoringList
    events={mockEvents}
    loading={isRefreshing}
   />
  </div>
 )
}
