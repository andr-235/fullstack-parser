import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, createQueryKey } from '@/shared/lib/api'
import type {
  ParseTaskCreate,
  ParseTaskResponse,
  PaginatedResponse,
  ParserState,
  ParserStats,
} from '@/types/api'
import { toast } from 'sonner'

/**
 * Хук для получения состояния парсера
 */
export function useParserState() {
  return useQuery<ParserState>({
    queryKey: createQueryKey.parserState(),
    queryFn: () => api.getParserState(),
    refetchInterval: 5000, // Опрашивать каждые 5 секунд
  })
}

/**
 * Хук для получения статистики парсера
 */
export function useParserStats() {
  return useQuery<ParserStats>({
    queryKey: createQueryKey.parserStats(),
    queryFn: () => api.getParserStats(),
    staleTime: 60 * 1000, // 1 минута
  })
}

/**
 * Хук для получения последних запусков парсера
 */
export function useRecentRuns() {
  return useQuery<PaginatedResponse<ParseTaskResponse>>({
    queryKey: createQueryKey.parserRuns(),
    queryFn: () => api.getRecentParseTasks(),
    staleTime: 30 * 1000, // 30 секунд
  })
}

/**
 * Хук для запуска новой задачи парсинга
 */
export function useStartParser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: ParseTaskCreate) => api.startParser(data),
    onSuccess: () => {
      toast.success('Парсинг запущен')
      queryClient.invalidateQueries({ queryKey: createQueryKey.parserState() })
      queryClient.invalidateQueries({ queryKey: createQueryKey.parserRuns() })
    },
    onError: (error: any) => {
      toast.error(`Ошибка запуска парсера: ${error.message}`)
    },
  })
}

/**
 * Хук для остановки парсера
 */
export function useStopParser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => api.stopParser(),
    onSuccess: () => {
      toast.info('Парсер останавливается...')
      queryClient.invalidateQueries({ queryKey: createQueryKey.parserState() })
    },
    onError: (error: any) => {
      toast.error(`Ошибка остановки парсера: ${error.message}`)
    },
  })
}
