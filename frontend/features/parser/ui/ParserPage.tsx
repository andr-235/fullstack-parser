'use client'

import { useState, useCallback, useEffect } from 'react'
import { Play, Square, RefreshCw, AlertCircle, Zap } from 'lucide-react'

import { Alert, AlertDescription, Button } from '@/shared/ui'
import { LiveStats } from './LiveStats'
import { ParserFilters } from './ParserFilters'
import { ParserModal } from './ParserModal'
import { ParserProgress } from './ParserProgress'
import { ParserQueue } from './ParserQueue'
import { useParser, useGroups, useStartParser } from '@/entities'

export function ParserPage() {
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<{ statuses?: string[] }>({})
  const [modalOpen, setModalOpen] = useState(false)

  const {
    state,
    stats,
    globalStats,
    tasks,
    isRunning,
    startParser,
    stopParser,
    loading,
    processing,
    refetch,
  } = useParser(0)

  const { startBulkParser } = useStartParser()

  const {
    groups,
    loading: groupsLoading,
    error: groupsError,
    refetch: refetchGroups,
  } = useGroups({ active_only: true, size: 10000 }, true)

  useEffect(() => {
    if (modalOpen && (!groups || groups.length === 0) && !groupsLoading) {
      refetchGroups()
    }
  }, [modalOpen, groups, groupsLoading, refetchGroups])

  const handleStopParser = useCallback(async () => {
    setError(null)
    try {
      await stopParser()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось остановить парсер')
    }
  }, [stopParser])

  const handleRefresh = useCallback(() => {
    refetch()
    refetchGroups()
  }, [refetch, refetchGroups])

  const handleStartParsing = useCallback(
    async (config: {
      groupId?: number | undefined
      parseAllGroups: boolean
      maxPosts: number
      forceReparse: boolean
    }) => {
      setError(null)

      try {
        if (config.parseAllGroups && (!groups || groups.length === 0)) {
          setError('Нет доступных активных групп для парсинга')
          return
        }

        if (config.groupId && (!groups || !groups.find(g => g.vk_id === config.groupId))) {
          setError('Выбранная группа не найдена')
          return
        }

        if (config.parseAllGroups) {
          const allGroupIds = groups?.map(g => g.vk_id) || []
          if (allGroupIds.length === 0) {
            setError('Нет доступных активных групп для парсинга')
            return
          }

          try {
            setError(`Запуск парсинга для ${allGroupIds.length} групп...`)
            const result = await startBulkParser({
              group_ids: allGroupIds,
              max_posts: config.maxPosts,
              force_reparse: config.forceReparse,
            })

            if (result.task_id) {
              setError(`Успешно запущена задача парсинга для ${allGroupIds.length} групп`)
            } else {
              setError('Задачи парсинга запущены, но не удалось получить ID задач')
            }
            refetch()
          } catch (batchError) {
            let errorMessage = 'Неизвестная ошибка'
            if (batchError instanceof Error) {
              errorMessage = batchError.message
            } else if (typeof batchError === 'string') {
              errorMessage = batchError
            } else if (batchError && typeof batchError === 'object') {
              if ('message' in batchError) {
                errorMessage = String(batchError.message)
              } else if ('detail' in batchError) {
                errorMessage = String(batchError.detail)
              } else if (
                'error' in batchError &&
                batchError.error &&
                typeof batchError.error === 'object' &&
                'message' in batchError.error
              ) {
                errorMessage = String(batchError.error.message)
              } else {
                try {
                  errorMessage = `Ошибка: ${JSON.stringify(batchError, null, 2)}`
                } catch {
                  errorMessage = `Ошибка: ${String(batchError)}`
                }
              }
            }
            setError(`Ошибка при запуске массового парсинга: ${errorMessage}`)
          }
        } else if (config.groupId) {
          await startParser({
            group_ids: [config.groupId],
            max_posts: config.maxPosts,
            force_reparse: config.forceReparse,
          })
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Не удалось запустить парсер')
      }
    },
    [groups, startParser, startBulkParser, refetch]
  )

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Парсер</h1>
            <p className="text-muted-foreground">Панель управления парсером комментариев VK</p>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                isRunning ? 'bg-green-500 animate-pulse' : error ? 'bg-red-500' : 'bg-gray-400'
              }`}
            />
            <span className="text-sm font-medium">
              {isRunning ? 'Активен' : error ? 'Ошибка' : 'Неактивен'}
            </span>
          </div>
        </div>

        <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
          <p className="text-sm text-blue-600 dark:text-blue-400">
            Автообновление отключено - используйте кнопку «Обновить данные»
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={handleRefresh}
            disabled={loading}
            className="gap-2 border-blue-200 hover:border-blue-300"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Обновить данные
          </Button>

          {!isRunning ? (
            <>
              <ParserModal
                groups={groups}
                stats={stats}
                onStartParsing={handleStartParsing}
                isOpen={modalOpen}
                onOpenChange={setModalOpen}
                trigger={
                  <Button disabled={processing || groupsLoading} className="gap-2">
                    <Play className="h-4 w-4" />
                    {processing ? 'Запуск...' : 'Запустить парсер'}
                  </Button>
                }
              />

              <Button
                onClick={() =>
                  handleStartParsing({
                    parseAllGroups: true,
                    maxPosts: 100,
                    forceReparse: false,
                  })
                }
                disabled={processing || groupsLoading || !groups || groups.length === 0}
                variant="secondary"
                className="gap-2"
              >
                <Zap className="h-4 w-4" />
                {groupsLoading
                  ? 'Загрузка...'
                  : processing
                    ? 'Запуск...'
                    : !groups || groups.length === 0
                      ? 'Нет групп'
                      : `Парсинг всех групп (${groups.length})`}
              </Button>
            </>
          ) : (
            <Button
              onClick={handleStopParser}
              variant="destructive"
              disabled={processing}
              className="gap-2"
            >
              <Square className="h-4 w-4" />
              {processing ? 'Остановка...' : 'Остановить парсер'}
            </Button>
          )}
        </div>
      </div>

      {error && (
        <Alert className="border-destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error}
            <Button variant="outline" size="sm" onClick={() => setError(null)} className="ml-4">
              Закрыть
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {groupsError && (
        <Alert className="border-yellow-500">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Ошибка загрузки групп: {groupsError}
            <Button variant="outline" size="sm" onClick={() => refetchGroups()} className="ml-4">
              Повторить
            </Button>
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <ParserProgress state={state} isRunning={isRunning ?? false} />
        </div>
        <div className="space-y-4">
          <LiveStats
            stats={stats}
            globalStats={globalStats}
            state={state}
            loading={loading}
            isRunning={isRunning ?? false}
          />
        </div>
      </div>

      <div className="space-y-4">
        <ParserQueue tasks={tasks} loading={loading} currentTaskId="" />
      </div>

      <div className="space-y-4">
        <ParserFilters filters={filters} onFiltersChange={setFilters} />
      </div>
    </div>
  )
}
