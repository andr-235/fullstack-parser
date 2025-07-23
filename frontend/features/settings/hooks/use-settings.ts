import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, createQueryKey } from '@/shared/lib/api'
import type {
  ApplicationSettings,
  SettingsUpdateRequest,
  SettingsResponse,
  SettingsHealthStatus,
} from '@/types/settings'
import { toast } from 'react-hot-toast'

/**
 * Хук для получения настроек приложения
 */
export function useSettings() {
  return useQuery<SettingsResponse>({
    queryKey: createQueryKey.settings(),
    queryFn: () => api.getSettings(),
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}

/**
 * Хук для обновления настроек
 */
export function useUpdateSettings() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (settings: SettingsUpdateRequest) =>
      api.updateSettings(settings),
    onSuccess: (data) => {
      queryClient.setQueryData(createQueryKey.settings(), data)
      queryClient.invalidateQueries({ queryKey: ['monitoring'] })
      queryClient.invalidateQueries({ queryKey: ['parser'] })
      toast.success('Настройки успешно обновлены')
    },
    onError: (error) => {
      console.error('Settings update error:', error)
      toast.error('Ошибка обновления настроек')
    },
  })
}

/**
 * Хук для сброса настроек к значениям по умолчанию
 */
export function useResetSettings() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => api.resetSettings(),
    onSuccess: (data) => {
      queryClient.setQueryData(createQueryKey.settings(), data)
      queryClient.invalidateQueries({ queryKey: ['monitoring'] })
      queryClient.invalidateQueries({ queryKey: ['parser'] })
      toast.success('Настройки сброшены к значениям по умолчанию')
    },
    onError: (error) => {
      console.error('Settings reset error:', error)
      toast.error('Ошибка сброса настроек')
    },
  })
}

/**
 * Хук для получения статуса здоровья настроек
 */
export function useSettingsHealth() {
  return useQuery<SettingsHealthStatus>({
    queryKey: createQueryKey.settingsHealth(),
    queryFn: () => api.getSettingsHealth(),
    staleTime: 30 * 1000, // 30 секунд
    refetchInterval: 60 * 1000, // Обновляем каждую минуту
  })
}

/**
 * Хук для тестирования подключения к VK API
 */
export function useTestVKAPIConnection() {
  return useMutation({
    mutationFn: ({
      accessToken,
      apiVersion,
    }: {
      accessToken: string
      apiVersion: string
    }) => api.testVKAPIConnection(accessToken, apiVersion),
    onSuccess: (isConnected) => {
      if (isConnected) {
        toast.success('Подключение к VK API успешно')
      } else {
        toast.error('Не удалось подключиться к VK API')
      }
    },
    onError: (error) => {
      console.error('VK API test error:', error)
      toast.error('Ошибка тестирования VK API')
    },
  })
}
