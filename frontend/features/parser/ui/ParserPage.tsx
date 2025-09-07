'use client'

import { useState, useCallback } from 'react'

import { Play, Square, RefreshCw, AlertCircle, Zap } from 'lucide-react'

import { Alert, AlertDescription } from '@/shared/ui'
import { Button } from '@/shared/ui'

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

    // Используем реальные хуки с автообновлением
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
    } = useParser(0) // Отключено автообновление

    const { startBulkParser } = useStartParser()



    // Получаем список групп для выбора (без автоматического запроса)
    const { groups, loading: groupsLoading, refetch: refetchGroups } = useGroups({
        active_only: true,
        size: 10000 // Получаем все активные группы
    }, false)

    const _handleStartParser = useCallback(async () => {
        if (!groups || groups.length === 0) {
            setError('Нет доступных активных групп для парсинга')
            return
        }

        setError(null)
        try {
            // Выбираем первую активную группу для примера
            const groupId = groups[0]?.id
            if (!groupId) {
                setError('Нет доступных активных групп для парсинга')
                return
            }

            await startParser({
                group_ids: [groupId],
                max_posts: 100,
                force_reparse: false,
            })
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Не удалось запустить парсер'
            setError(errorMessage)
            // console.error('Failed to start parser:', err)
        }
    }, [groups, startParser])

    const handleStopParser = useCallback(async () => {
        setError(null)
        try {
            await stopParser()
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Не удалось остановить парсер'
            setError(errorMessage)
            // console.error('Failed to stop parser:', err)
        }
    }, [stopParser])

    const handleRefresh = useCallback(() => {
        refetch()
        refetchGroups()
    }, [refetch, refetchGroups])

    const handleStartParsing = useCallback(async (config: {
        groupId?: number | undefined
        parseAllGroups: boolean
        maxPosts: number
        forceReparse: boolean
    }) => {
        setError(null)
        try {
            // Проверяем наличие групп перед запуском
            if (config.parseAllGroups && (!groups || groups.length === 0)) {
                setError('Нет доступных активных групп для парсинга')
                return
            }

            // Проверяем лимит групп для массового парсинга
            if (config.parseAllGroups && groups && stats && groups.length > stats.max_groups_per_request) {
                setError(`Слишком много групп для парсинга (${groups.length}). Максимум ${stats.max_groups_per_request} групп за раз.`)
                return
            }
            if (config.groupId && (!groups || !groups.find(g => g.id === config.groupId))) {
                setError('Выбранная группа не найдена')
                return
            }
            if (config.parseAllGroups) {
                // Запуск массового парсинга всех групп через backend API
                const allGroupIds = groups?.map(g => g.id) || []

                if (allGroupIds.length === 0) {
                    setError('Нет доступных активных групп для парсинга')
                    return
                }

                // Разбиваем группы на батчи по 100 штук (лимит API)
                const BATCH_SIZE = 100
                const batches: number[][] = []

                for (let i = 0; i < allGroupIds.length; i += BATCH_SIZE) {
                    batches.push(allGroupIds.slice(i, i + BATCH_SIZE))
                }

                try {
                    const results = []

                    // Запускаем парсинг для каждого батча
                    for (let i = 0; i < batches.length; i++) {
                        const batch = batches[i]

                        if (!batch || batch.length === 0) {
                            continue
                        }

                        // Обновляем сообщение о прогрессе
                        setError(`Запуск парсинга батча ${i + 1}/${batches.length} (${batch.length} групп)...`)

                        const result = await startBulkParser({
                            group_ids: batch,
                            max_posts: config.maxPosts,
                            force_reparse: config.forceReparse,
                        })

                        results.push(result)

                        // Небольшая задержка между батчами, чтобы не перегружать API
                        if (i < batches.length - 1) {
                            await new Promise(resolve => setTimeout(resolve, 1000))
                        }
                    }

                    // Показываем результат массового парсинга
                    const totalTasks = results.filter(r => r.task_id).length
                    if (totalTasks > 0) {
                        setError(`Успешно запущено ${totalTasks} задач парсинга для ${allGroupIds.length} групп`)
                    } else {
                        setError('Задачи парсинга запущены, но не удалось получить ID задач')
                    }

                    // Обновляем состояние сразу после запуска
                    refetch()
                } catch (batchError) {
                    setError(`Ошибка при запуске массового парсинга: ${batchError instanceof Error ? batchError.message : 'Неизвестная ошибка'}`)
                }
            } else if (config.groupId) {
                // Запуск парсинга одной группы
                await startParser({
                    group_ids: [config.groupId],
                    max_posts: config.maxPosts,
                    force_reparse: config.forceReparse,
                })
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Не удалось запустить парсер'
            setError(errorMessage)
            // console.error('Failed to start parser:', err)
        }
    }, [groups, stats, startParser, startBulkParser, refetch])

    return (
        <div className="container mx-auto py-8 space-y-8">
            {/* Header */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Парсер</h1>
                        <p className="text-muted-foreground">
                            Панель управления парсером комментариев VK
                        </p>
                    </div>

                    {/* Статус индикатор */}
                    <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-green-500 animate-pulse' :
                            error ? 'bg-red-500' :
                                'bg-gray-400'
                            }`} />
                        <span className="text-sm font-medium">
                            {isRunning ? 'Активен' :
                                error ? 'Ошибка' :
                                    'Неактивен'}
                        </span>
                    </div>
                </div>

                {/* Уведомление об отключенном автообновлении */}
                <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                    <p className="text-sm text-blue-600 dark:text-blue-400">
                        Автообновление отключено - используйте кнопку «Обновить данные»
                    </p>
                </div>

                {/* Кнопки управления */}
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
                                    <Button
                                        disabled={processing || groupsLoading}
                                        className="gap-2"
                                    >
                                        <Play className="h-4 w-4" />
                                        {processing ? 'Запуск...' : 'Запустить парсер'}
                                    </Button>
                                }
                            />

                            <Button
                                onClick={() => handleStartParsing({
                                    parseAllGroups: true,
                                    maxPosts: 100,
                                    forceReparse: false
                                })}
                                disabled={processing || groupsLoading || !groups || groups.length === 0}
                                variant="secondary"
                                className="gap-2"
                            >
                                <Zap className="h-4 w-4" />
                                {groupsLoading ? 'Загрузка...' :
                                    processing ? 'Запуск...' :
                                        !groups || groups.length === 0 ? 'Нет групп' :
                                            `Парсинг всех групп (${groups.length})`}
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

            {/* Error State */}
            {error && (
                <Alert className="border-destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                        {error}
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setError(null)}
                            className="ml-4"
                        >
                            Закрыть
                        </Button>
                    </AlertDescription>
                </Alert>
            )}

            {/* Основная информация */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Детальный прогресс парсинга */}
                <div className="space-y-4">
                    <ParserProgress
                        state={state}
                        isRunning={isRunning ?? false}
                    />
                </div>

                {/* Статистика в реальном времени */}
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

            {/* Очередь задач */}
            <div className="space-y-4">
                <ParserQueue
                    tasks={tasks}
                    loading={loading}
                    currentTaskId=""
                />
            </div>

            {/* Настройки и управление */}
            <div className="space-y-4">
                <ParserFilters filters={filters} onFiltersChange={setFilters} />
            </div>
        </div>
    )
}
