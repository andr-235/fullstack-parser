import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, createQueryKey } from '@/shared/lib/api'

interface ErrorReport {
  report_id: string
  created_at: string
  operation: string
  total_errors: number
  errors: Array<{
    timestamp: string
    error_type: string
    severity: string
    message: string
    details?: string
    context?: any
    stack_trace?: string
  }>
  summary: Record<string, number>
  recommendations: string[]
  groups_processed?: number
  groups_successful?: number
  groups_failed?: number
  groups_skipped?: number
  processing_time_seconds?: number
}

interface ErrorReportFilters {
  error_type?: string
  severity?: string
  operation?: string
  start_date?: string
  end_date?: string
  page?: number
  size?: number
}

interface ErrorStats {
  period: {
    start_date: string
    end_date: string
  }
  total_errors: number
  errors_by_type: Record<string, number>
  errors_by_severity: Record<string, number>
  errors_by_operation: Record<string, number>
  trends: {
    daily: Array<{ date: string; count: number }>
    hourly: Array<{ hour: string; count: number }>
  }
}

/**
 * Хук для получения списка отчетов об ошибках
 */
export function useErrorReports(filters?: ErrorReportFilters) {
  return useQuery({
    queryKey: createQueryKey.errorReports(filters),
    queryFn: () => api.getErrorReports(filters),
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}

/**
 * Хук для получения конкретного отчета об ошибках
 */
export function useErrorReport(reportId: string) {
  return useQuery({
    queryKey: createQueryKey.errorReport(reportId),
    queryFn: () => api.getErrorReport(reportId),
    enabled: !!reportId,
    staleTime: 5 * 60 * 1000,
  })
}

/**
 * Хук для получения статистики ошибок
 */
export function useErrorStats(days: number = 7) {
  return useQuery({
    queryKey: createQueryKey.errorStats(days),
    queryFn: () => api.getErrorStats(days),
    staleTime: 10 * 60 * 1000, // 10 минут
  })
}

/**
 * Хук для подтверждения обработки отчета
 */
export function useAcknowledgeErrorReport() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (reportId: string) => api.acknowledgeErrorReport(reportId),
    onSuccess: (data, reportId) => {
      // Инвалидируем кеш отчетов
      queryClient.invalidateQueries({
        queryKey: createQueryKey.errorReports(),
      })

      // Обновляем конкретный отчет
      queryClient.setQueryData(createQueryKey.errorReport(reportId), data)
    },
  })
}

/**
 * Хук для удаления отчета
 */
export function useDeleteErrorReport() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (reportId: string) => api.deleteErrorReport(reportId),
    onSuccess: (_, reportId) => {
      // Инвалидируем кеш отчетов
      queryClient.invalidateQueries({
        queryKey: createQueryKey.errorReports(),
      })

      // Удаляем отчет из кеша
      queryClient.removeQueries({
        queryKey: createQueryKey.errorReport(reportId),
      })
    },
  })
}
