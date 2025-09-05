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



    // Получаем список групп для выбора
    const { groups, loading: groupsLoading } = useGroups({
        active_only: true,
        size: 100 // Получаем все активные группы
    })

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
    }, [refetch])

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
            if (config.groupId && (!groups || !groups.find(g => g.id === config.groupId))) {
                setError('Выбранная группа не найдена')
                return
            }
            if (config.parseAllGroups) {
                // Запуск массового парсинга всех групп через backend API
                // console.log('Starting bulk parser with config:', config)
                // console.log('Available groups:', groups?.length || 0)

                const result = await startBulkParser({
                    group_ids: groups?.map(g => g.id) || [],
                    max_posts: config.maxPosts,
                    force_reparse: config.forceReparse,
                })

                // console.log('Bulk parser result:', result)

                // Показываем результат массового парсинга
                if (result.task_id) {
                    setError(`Успешно запущена задача парсинга с ID: ${result.task_id}`)
                } else {
                    setError('Задача парсинга запущена, но не удалось получить ID задачи')
                }

                // Обновляем состояние через некоторое время
                setTimeout(() => refetch(), 2000)
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
    }, [groups, startParser, startBulkParser, refetch])

    return (
        <div className="container mx-auto py-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Парсер</h1>
                        <p className="text-muted-foreground">
                            Панель управления парсером комментариев VK
                        </p>
                        <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                            Автообновление отключено - используйте кнопку «Обновить данные»
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
                <div>
                    <ParserProgress
                        state={state}
                        isRunning={isRunning ?? false}
                    />
                </div>

                {/* Статистика в реальном времени */}
                <div>
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
            <ParserQueue
                tasks={tasks}
                loading={loading}
                currentTaskId=""
            />

            {/* Настройки и управление */}
            <div className="grid grid-cols-1 gap-6">
                <ParserFilters filters={filters} onFiltersChange={setFilters} />
            </div>
        </div>
    )
}
