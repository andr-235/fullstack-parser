'use client'

import { useState } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LoadingSpinnerWithText } from '@/components/ui/loading-spinner'
import {
  Play,
  Pause,
  Square,
  Settings,
  Clock,
  Activity,
  AlertCircle,
  CheckCircle,
  Info,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Loader,
} from 'lucide-react'

// Моковые данные состояния парсера
const mockParserState = {
  is_running: false,
  current_task: null,
  last_run_time: '2024-01-15T14:30:00Z',
  total_runs: 47,
  success_rate: 98.2,
  avg_duration: 342, // seconds
  errors_count: 2,
  groups_in_queue: 5,
  estimated_completion: null,
}

const mockRecentRuns = [
  {
    id: 1,
    start_time: '2024-01-15T14:30:00Z',
    end_time: '2024-01-15T14:35:42Z',
    status: 'completed',
    groups_processed: 12,
    comments_found: 89,
    errors: 0,
    duration: 342,
  },
  {
    id: 2,
    start_time: '2024-01-15T12:15:00Z',
    end_time: '2024-01-15T12:20:31Z',
    status: 'completed',
    groups_processed: 8,
    comments_found: 45,
    errors: 0,
    duration: 331,
  },
  {
    id: 3,
    start_time: '2024-01-15T10:00:00Z',
    end_time: '2024-01-15T10:05:15Z',
    status: 'failed',
    groups_processed: 3,
    comments_found: 12,
    errors: 2,
    duration: 315,
  },
]

// Mock parsing function
const startParsing = () => new Promise((resolve) => setTimeout(resolve, 2000))

export default function ParserPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [parserState, setParserState] = useState(mockParserState)
  const [showSettings, setShowSettings] = useState(false)
  const [isParsing, setIsParsing] = useState(false)
  const [parseResult, setParseResult] = useState<'success' | 'error' | null>(
    null
  )

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInMinutes = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60)
    )

    if (diffInMinutes < 60) return `${diffInMinutes} мин назад`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} ч назад`
    return `${Math.floor(diffInMinutes / 1440)} дн назад`
  }

  const handleStartParser = async () => {
    setIsLoading(true)
    setIsParsing(true)
    setParseResult(null)
    try {
      await startParsing()
      setParseResult('success')
      setParserState((prev) => ({ ...prev, is_running: true }))
    } catch (err) {
      setParseResult('error')
    } finally {
      setIsLoading(false)
      setIsParsing(false)
    }
  }

  const handleStopParser = async () => {
    setIsLoading(true)
    try {
      // TODO: API call
      console.log('Stopping parser...')
      setParserState((prev) => ({ ...prev, is_running: false }))
    } catch (error) {
      console.error('Failed to stop parser:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-600" />
      case 'running':
        return <Activity className="h-4 w-4 text-blue-600" />
      default:
        return <Info className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success'
      case 'failed':
        return 'destructive'
      case 'running':
        return 'default'
      default:
        return 'secondary'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Управление парсингом
          </h1>
          <p className="text-gray-600 mt-2">
            Запуск и мониторинг парсинга комментариев ВКонтакте
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings className="h-4 w-4 mr-2" />
            Настройки
          </Button>
          <Button variant="outline" disabled={isLoading}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Обновить
          </Button>
        </div>
      </div>

      {/* Current Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <Activity className="h-5 w-5" />
            Текущий статус парсера
            <Badge variant={parserState.is_running ? 'default' : 'secondary'}>
              {parserState.is_running ? 'Запущен' : 'Остановлен'}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Control Panel */}
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900">Управление</h3>
              <div className="space-y-2">
                {!parserState.is_running ? (
                  <Button
                    onClick={handleStartParser}
                    disabled={isLoading}
                    className="w-full"
                  >
                    {isParsing ? (
                      <LoadingSpinnerWithText text="" size="sm" />
                    ) : (
                      <Play className="h-4 w-4 mr-2" />
                    )}
                    Запустить парсинг
                  </Button>
                ) : (
                  <div className="space-y-2">
                    <Button
                      variant="secondary"
                      onClick={handleStopParser}
                      disabled={isLoading}
                      className="w-full"
                    >
                      {isLoading ? (
                        <LoadingSpinnerWithText text="" size="sm" />
                      ) : (
                        <Pause className="h-4 w-4 mr-2" />
                      )}
                      Приостановить
                    </Button>
                    <Button
                      variant="destructive"
                      onClick={handleStopParser}
                      disabled={isLoading}
                      className="w-full"
                    >
                      <Square className="h-4 w-4 mr-2" />
                      Остановить
                    </Button>
                  </div>
                )}
              </div>
            </div>

            {/* Current Task */}
            <div className="space-y-2">
              <h3 className="font-semibold text-gray-900">Текущая задача</h3>
              <div className="text-sm space-y-1">
                {parserState.current_task ? (
                  <>
                    <p className="text-gray-900">{parserState.current_task}</p>
                    <p className="text-gray-600">Группа: Барахолка СПб</p>
                    <p className="text-gray-600">Прогресс: 67%</p>
                  </>
                ) : (
                  <p className="text-gray-600">Нет активных задач</p>
                )}
              </div>
            </div>

            {/* Statistics */}
            <div className="space-y-2">
              <h3 className="font-semibold text-gray-900">Статистика</h3>
              <div className="text-sm space-y-1">
                <p className="text-gray-600">
                  Всего запусков:{' '}
                  <span className="text-gray-900 font-medium">
                    {parserState.total_runs}
                  </span>
                </p>
                <p className="text-gray-600">
                  Успешность:{' '}
                  <span className="text-green-600 font-medium">
                    {parserState.success_rate}%
                  </span>
                </p>
                <p className="text-gray-600">
                  Средняя длительность:{' '}
                  <span className="text-gray-900 font-medium">
                    {formatDuration(parserState.avg_duration)}
                  </span>
                </p>
                <p className="text-gray-600">
                  Ошибки:{' '}
                  <span className="text-red-600 font-medium">
                    {parserState.errors_count}
                  </span>
                </p>
              </div>
            </div>

            {/* Queue Info */}
            <div className="space-y-2">
              <h3 className="font-semibold text-gray-900">Очередь</h3>
              <div className="text-sm space-y-1">
                <p className="text-gray-600">
                  Групп в очереди:{' '}
                  <span className="text-blue-600 font-medium">
                    {parserState.groups_in_queue}
                  </span>
                </p>
                <p className="text-gray-600">
                  Последний запуск:{' '}
                  <span className="text-gray-900 font-medium">
                    {formatRelativeTime(parserState.last_run_time)}
                  </span>
                </p>
                {parserState.estimated_completion && (
                  <p className="text-gray-600">
                    Завершение:{' '}
                    <span className="text-orange-600 font-medium">
                      {formatRelativeTime(parserState.estimated_completion)}
                    </span>
                  </p>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Settings Panel (if shown) */}
      {showSettings && (
        <Card>
          <CardHeader>
            <CardTitle>Настройки парсера</CardTitle>
            <CardDescription>
              Конфигурация параметров парсинга и расписания
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Интервал парсинга (минуты)
                  </label>
                  <input
                    type="number"
                    defaultValue={30}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Максимум групп за раз
                  </label>
                  <input
                    type="number"
                    defaultValue={10}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      defaultChecked
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">
                      Автоматический запуск
                    </span>
                  </label>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Время начала (UTC)
                  </label>
                  <input
                    type="time"
                    defaultValue="09:00"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Время окончания (UTC)
                  </label>
                  <input
                    type="time"
                    defaultValue="18:00"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      defaultChecked
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">
                      Уведомления об ошибках
                    </span>
                  </label>
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6 pt-6 border-t">
              <Button variant="outline" onClick={() => setShowSettings(false)}>
                Отмена
              </Button>
              <Button>Сохранить настройки</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Runs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Последние запуски
          </CardTitle>
          <CardDescription>
            История запусков парсера за последние 24 часа
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockRecentRuns.map((run) => (
              <div
                key={run.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(run.status)}
                    <Badge variant={getStatusColor(run.status)}>
                      {run.status === 'completed'
                        ? 'Завершен'
                        : run.status === 'failed'
                          ? 'Ошибка'
                          : run.status === 'running'
                            ? 'Выполняется'
                            : 'Неизвестно'}
                    </Badge>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {formatRelativeTime(run.start_time)}
                    </p>
                    <p className="text-xs text-gray-600">
                      Длительность: {formatDuration(run.duration)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-6 text-sm">
                  <div className="text-center">
                    <p className="text-gray-600">Групп</p>
                    <p className="font-medium">{run.groups_processed}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-gray-600">Комментариев</p>
                    <p className="font-medium">{run.comments_found}</p>
                  </div>
                  {run.errors > 0 && (
                    <div className="text-center">
                      <p className="text-red-600">Ошибок</p>
                      <p className="font-medium text-red-600">{run.errors}</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Производительность</CardTitle>
            <CardDescription>Метрики работы парсера</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">
                  Комментариев в час
                </span>
                <span className="text-sm font-medium">~156</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Групп в час</span>
                <span className="text-sm font-medium">~24</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Загрузка CPU</span>
                <span className="text-sm font-medium">23%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Использование RAM</span>
                <span className="text-sm font-medium">156 MB</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Настройки качества</CardTitle>
            <CardDescription>Параметры точности парсинга</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Глубина поиска</span>
                <Badge variant="outline">100 постов</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">
                  Лимит комментариев
                </span>
                <Badge variant="outline">1000 на пост</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Фильтр спама</span>
                <Badge variant="success">Включен</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Дубликаты</span>
                <Badge variant="success">Исключены</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {parseResult && (
        <div className="mt-6 w-full">
          {parseResult === 'success' && (
            <div role="alert" className="alert alert-success">
              <CheckCircle2 size={24} />
              <span>
                Парсинг успешно завершен! Новые комментарии добавлены.
              </span>
            </div>
          )}
          {parseResult === 'error' && (
            <div role="alert" className="alert alert-error">
              <XCircle size={24} />
              <span>Произошла ошибка во время парсинга. Попробуйте позже.</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
