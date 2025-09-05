import { useState, useEffect, useCallback } from 'react'

import { apiClient } from '@/shared/lib'

import {
  ParseTaskCreate,
  ParserState,
  ParserStats,
  ParserGlobalStats,
  ParserTasksResponse,
  ParserHistoryResponse,
  ParserTaskFilters,
  StartBulkParserForm,
  BulkParseResponse,
  ParseStatus,
  StopParseRequest,
} from './types'

// Хук для управления состоянием парсера
export const useParserState = (autoFetch: boolean = true) => {
  const [state, setState] = useState<ParserState | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchState = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.getParserState()
      setState(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch parser state')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (autoFetch) {
      fetchState()
    }
  }, [fetchState, autoFetch])

  return {
    state,
    loading,
    error,
    refetch: fetchState,
  }
}

// Хук для статистики парсера
export const useParserStats = (autoFetch: boolean = true) => {
  const [stats, setStats] = useState<ParserStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.getParserStats()
      setStats(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch parser stats')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (autoFetch) {
      fetchStats()
    }
  }, [fetchStats, autoFetch])

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  }
}

// Хук для глобальной статистики парсера
export const useParserGlobalStats = (autoFetch: boolean = true) => {
  const [stats, setStats] = useState<ParserGlobalStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.getParserGlobalStats()
      setStats(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch parser global stats')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (autoFetch) {
      fetchStats()
    }
  }, [fetchStats, autoFetch])

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  }
}

// Хук для управления задачами парсера
export const useParserTasks = (filters?: ParserTaskFilters, autoFetch: boolean = true) => {
  const [tasks, setTasks] = useState<ParserTasksResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchTasks = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.getParserTasks(filters)
      setTasks(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch parser tasks')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    if (autoFetch) {
      fetchTasks()
    }
  }, [fetchTasks, autoFetch])

  return {
    tasks,
    loading,
    error,
    refetch: fetchTasks,
  }
}

// Хук для получения конкретной задачи парсера
export const useParserTask = (taskId: string) => {
  const [task, setTask] = useState<ParseStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchTask = useCallback(async () => {
    if (!taskId) return

    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.getParserTask(taskId)
      setTask(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch parser task')
    } finally {
      setLoading(false)
    }
  }, [taskId])

  useEffect(() => {
    fetchTask()
  }, [fetchTask])

  return {
    task,
    loading,
    error,
    refetch: fetchTask,
  }
}

// Хук для истории парсера
export const useParserHistory = (page = 1, size = 10) => {
  const [history, setHistory] = useState<ParserHistoryResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchHistory = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.getParserHistory(page, size)
      setHistory(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch parser history')
    } finally {
      setLoading(false)
    }
  }, [page, size])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  return {
    history,
    loading,
    error,
    refetch: fetchHistory,
  }
}

// Хук для запуска парсера
export const useStartParser = () => {
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const startParser = useCallback(async (taskData: ParseTaskCreate) => {
    setStarting(true)
    setError(null)
    try {
      const result = await apiClient.startParser(taskData)
      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start parser'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setStarting(false)
    }
  }, [])

  const startBulkParser = useCallback(
    async (bulkData: StartBulkParserForm): Promise<BulkParseResponse> => {
      setStarting(true)
      setError(null)
      try {
        const result = await apiClient.startBulkParser(bulkData)
        return result
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to start bulk parser'
        setError(errorMessage)
        throw new Error(errorMessage)
      } finally {
        setStarting(false)
      }
    },
    []
  )

  return {
    startParser,
    startBulkParser,
    starting,
    error,
  }
}

// Хук для остановки парсера
export const useStopParser = () => {
  const [stopping, setStopping] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const stopParser = useCallback(async (request: StopParseRequest = {}) => {
    setStopping(true)
    setError(null)
    try {
      const result = await apiClient.stopParser(request)
      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to stop parser'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setStopping(false)
    }
  }, [])

  return {
    stopParser,
    stopping,
    error,
  }
}

// Хук для автоматического обновления данных
export const useAutoRefresh = (_intervalMs: number = 5000, enabled: boolean = true) => {
  const [isEnabled, setIsEnabled] = useState(enabled)

  const toggleAutoRefresh = useCallback(() => {
    setIsEnabled(prev => !prev)
  }, [])

  return {
    isEnabled,
    toggleAutoRefresh,
  }
}

// Хук для управления парсером (комбинированный)
export const useParser = (autoRefreshInterval: number = 3000) => {
  const {
    state,
    loading: stateLoading,
    refetch: refetchState,
  } = useParserState(autoRefreshInterval > 0)
  const {
    stats,
    loading: statsLoading,
    refetch: refetchStats,
  } = useParserStats(autoRefreshInterval > 0)
  const {
    stats: globalStats,
    loading: globalStatsLoading,
    refetch: refetchGlobalStats,
  } = useParserGlobalStats(autoRefreshInterval > 0)
  const { startParser, starting } = useStartParser()
  const { stopParser, stopping } = useStopParser()
  const { tasks, refetch: refetchTasks } = useParserTasks({ size: 10 }, autoRefreshInterval > 0)

  // Если автообновление отключено, делаем только один запрос при инициализации
  useEffect(() => {
    if (autoRefreshInterval <= 0) {
      // Делаем только один запрос при инициализации, если автообновление отключено
      refetchState()
      refetchStats()
      refetchGlobalStats()
      refetchTasks()
    }
  }, [autoRefreshInterval, refetchState, refetchStats, refetchGlobalStats, refetchTasks])

  const isRunning = Boolean(state?.is_running && state.active_tasks > 0)
  const isStopped = Boolean(!state?.is_running && state?.active_tasks === 0)
  const hasError = false // В новом API статус ошибки не определен в ParserState

  const loading = stateLoading || statsLoading || globalStatsLoading
  const processing = starting || stopping

  // Счетчик ошибок для остановки автообновления
  const [errorCount, setErrorCount] = useState(0)
  const MAX_ERRORS = 5 // Максимум ошибок подряд перед остановкой автообновления

  // Автоматическое обновление данных (отключено если autoRefreshInterval = 0)
  useEffect(() => {
    if (!isRunning || errorCount >= MAX_ERRORS || autoRefreshInterval <= 0) return

    const interval = setInterval(() => {
      // Добавляем обработку ошибок для предотвращения бесконечных запросов
      Promise.all([
        refetchState().catch(_err => {
          // console.warn('Failed to refetch parser state:', err)
          setErrorCount(prev => prev + 1)
        }),
        refetchStats().catch(_err => {
          // console.warn('Failed to refetch parser stats:', err)
          setErrorCount(prev => prev + 1)
        }),
        refetchGlobalStats().catch(_err => {
          // console.warn('Failed to refetch global stats:', err)
          setErrorCount(prev => prev + 1)
        }),
        refetchTasks().catch(_err => {
          // console.warn('Failed to refetch parser tasks:', err)
          setErrorCount(prev => prev + 1)
        }),
      ]).then(() => {
        // Сбрасываем счетчик ошибок при успешном обновлении
        setErrorCount(0)
      })
    }, autoRefreshInterval)

    return () => clearInterval(interval)
  }, [
    isRunning,
    autoRefreshInterval,
    refetchState,
    refetchStats,
    refetchGlobalStats,
    refetchTasks,
    errorCount,
  ])

  const refetch = useCallback(() => {
    refetchState()
    refetchStats()
    refetchGlobalStats()
    refetchTasks()
  }, [refetchState, refetchStats, refetchGlobalStats, refetchTasks])

  return {
    // State
    state,
    stats,
    globalStats,
    tasks,
    isRunning,
    isStopped,
    hasError,

    // Actions
    startParser,
    stopParser,

    // Status
    loading,
    processing,
    starting,
    stopping,

    // Utils
    refetch,
  }
}
