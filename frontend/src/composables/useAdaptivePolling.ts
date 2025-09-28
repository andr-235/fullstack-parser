import { ref, computed, onUnmounted, readonly } from 'vue'
import type { Ref, ComputedRef } from 'vue'

/**
 * Конфигурация для адаптивного polling
 */
export interface PollingConfig {
  /** Базовый интервал polling в миллисекундах */
  baseInterval: number
  /** Максимальный интервал polling в миллисекундах */
  maxInterval: number
  /** Множитель для exponential backoff */
  backoffMultiplier: number
  /** Максимальное количество попыток повтора при ошибке */
  maxRetries: number
  /** Тип задачи для настройки специфичных параметров */
  taskType: 'vk-collect' | 'export' | 'general'
}

/**
 * Результат выполнения polling функции
 */
export interface PollingResult {
  /** Статус задачи */
  status: 'pending' | 'processing' | 'completed' | 'failed'
  /** Дополнительные данные задачи */
  [key: string]: any
}

/**
 * Функция для выполнения polling запроса
 */
export type PollingFunction = () => Promise<PollingResult>

/**
 * Возвращаемые данные из composable
 */
export interface UseAdaptivePollingReturn {
  /** Активен ли polling в данный момент */
  isPolling: ComputedRef<boolean>
  /** Текущий интервал polling в миллисекундах */
  currentInterval: ComputedRef<number>
  /** Количество неудачных попыток */
  retryCount: ComputedRef<number>
  /** Последняя ошибка polling */
  lastError: ComputedRef<string | null>
  /** Текущий статус задачи */
  currentStatus: ComputedRef<string | null>
  /** Запуск polling */
  startPolling: (pollFunction: PollingFunction) => Promise<void>
  /** Остановка polling */
  stopPolling: () => void
  /** Сброс счетчика ошибок и интервала */
  resetPolling: () => void
}

/**
 * Предустановленные конфигурации для разных типов задач
 */
const POLLING_CONFIGS: Record<string, PollingConfig> = {
  'vk-collect': {
    baseInterval: 2000,      // 2 секунды для VK задач
    maxInterval: 30000,      // Максимум 30 секунд
    backoffMultiplier: 1.5,  // Плавное увеличение
    maxRetries: 5,
    taskType: 'vk-collect'
  },
  'export': {
    baseInterval: 5000,      // 5 секунд для экспорта
    maxInterval: 60000,      // Максимум 1 минута
    backoffMultiplier: 2,    // Более агрессивное увеличение
    maxRetries: 3,
    taskType: 'export'
  },
  'general': {
    baseInterval: 3000,      // 3 секунды для общих задач
    maxInterval: 15000,      // Максимум 15 секунд
    backoffMultiplier: 1.3,  // Умеренное увеличение
    maxRetries: 5,
    taskType: 'general'
  }
}

/**
 * Composable для адаптивного polling с exponential backoff
 *
 * @param taskId ID задачи для отслеживания
 * @param taskType Тип задачи для выбора подходящей конфигурации
 * @param customConfig Пользовательская конфигурация (переопределяет предустановленную)
 */
export function useAdaptivePolling(
  taskId: string | ComputedRef<string>,
  taskType: string = 'general',
  customConfig?: Partial<PollingConfig>
): UseAdaptivePollingReturn {
  // Получаем базовую конфигурацию и применяем пользовательские настройки
  const baseConfig = POLLING_CONFIGS[taskType] || POLLING_CONFIGS.general
  const config: PollingConfig = {
    baseInterval: customConfig?.baseInterval ?? baseConfig?.baseInterval ?? 3000,
    maxInterval: customConfig?.maxInterval ?? baseConfig?.maxInterval ?? 15000,
    backoffMultiplier: customConfig?.backoffMultiplier ?? baseConfig?.backoffMultiplier ?? 1.3,
    maxRetries: customConfig?.maxRetries ?? baseConfig?.maxRetries ?? 5,
    taskType: customConfig?.taskType ?? baseConfig?.taskType ?? 'general'
  }

  // Reactive состояние
  const isPolling = ref(false)
  const currentInterval = ref(config.baseInterval)
  const retryCount = ref(0)
  const lastError = ref<string | null>(null)
  const currentStatus = ref<string | null>(null)

  // Таймер для polling
  let pollingTimeout: NodeJS.Timeout | null = null

  // Computed свойства
  const shouldContinuePolling = computed(() => {
    // Продолжаем polling если:
    // 1. Polling активен
    // 2. Не превышено максимальное количество попыток
    // 3. Задача не завершена и не провалена
    return isPolling.value &&
           retryCount.value < config.maxRetries &&
           !['completed', 'failed'].includes(currentStatus.value || '')
  })

  /**
   * Запуск адаптивного polling
   */
  const startPolling = async (pollFunction: PollingFunction): Promise<void> => {
    // Если polling уже активен, не запускаем новый
    if (isPolling.value) {
      console.warn(`Polling уже активен для задачи ${taskId}`)
      return
    }

    isPolling.value = true
    retryCount.value = 0
    currentInterval.value = config.baseInterval
    lastError.value = null

    console.log(`Запуск адаптивного polling для задачи ${taskId} (тип: ${taskType})`)

    const poll = async (): Promise<void> => {
      // Проверяем, нужно ли продолжать polling
      if (!shouldContinuePolling.value) {
        console.log(`Останавливаем polling для задачи ${taskId}: условие не выполнено`)
        stopPolling()
        return
      }

      try {
        console.debug(`Polling попытка для задачи ${taskId}, интервал: ${currentInterval.value}ms`)

        // Выполняем polling функцию
        const result = await pollFunction()
        currentStatus.value = result.status

        // При успешном запросе сбрасываем счетчики ошибок
        if (retryCount.value > 0) {
          console.log(`Успешный запрос после ${retryCount.value} ошибок, сбрасываем интервал`)
          retryCount.value = 0
          currentInterval.value = config.baseInterval
          lastError.value = null
        }

        // Проверяем статус задачи
        if (['completed', 'failed'].includes(result.status)) {
          console.log(`Задача ${taskId} завершена со статусом: ${result.status}`)
          stopPolling()
          return
        }

      } catch (error: any) {
        retryCount.value++
        lastError.value = error?.message || 'Неизвестная ошибка polling'

        // Увеличиваем интервал при ошибке (exponential backoff)
        const newInterval = Math.min(
          currentInterval.value * config.backoffMultiplier,
          config.maxInterval
        )

        console.warn(
          `Ошибка polling для задачи ${taskId} (попытка ${retryCount.value}/${config.maxRetries}):`,
          error?.message,
          `Новый интервал: ${newInterval}ms`
        )

        currentInterval.value = newInterval

        // Если превышено максимальное количество попыток, останавливаем polling
        if (retryCount.value >= config.maxRetries) {
          console.error(`Превышено максимальное количество попыток polling для задачи ${taskId}`)
          stopPolling()
          return
        }
      }

      // Планируем следующий запрос с текущим интервалом
      if (shouldContinuePolling.value) {
        pollingTimeout = setTimeout(poll, currentInterval.value)
      }
    }

    // Запускаем первый polling
    await poll()
  }

  /**
   * Остановка polling
   */
  const stopPolling = (): void => {
    if (!isPolling.value) return

    console.log(`Остановка polling для задачи ${taskId}`)

    isPolling.value = false

    if (pollingTimeout) {
      clearTimeout(pollingTimeout)
      pollingTimeout = null
    }
  }

  /**
   * Сброс состояния polling (полезно для перезапуска)
   */
  const resetPolling = (): void => {
    stopPolling()
    retryCount.value = 0
    currentInterval.value = config.baseInterval
    lastError.value = null
    currentStatus.value = null
  }

  // Автоматическая очистка при размонтировании компонента
  onUnmounted(() => {
    console.log(`Автоматическая остановка polling при размонтировании (задача ${taskId})`)
    stopPolling()
  })

  return {
    // Computed свойства для ReactiveEffect
    isPolling: computed(() => isPolling.value),
    currentInterval: computed(() => currentInterval.value),
    retryCount: computed(() => retryCount.value),
    lastError: computed(() => lastError.value),
    currentStatus: computed(() => currentStatus.value),

    // Методы управления
    startPolling,
    stopPolling,
    resetPolling
  }
}

/**
 * Утилитарная функция для получения конфигурации polling по типу задачи
 */
export function getPollingConfig(taskType: string): PollingConfig {
  const config = POLLING_CONFIGS[taskType] || POLLING_CONFIGS.general
  return {
    baseInterval: config?.baseInterval ?? 3000,
    maxInterval: config?.maxInterval ?? 15000,
    backoffMultiplier: config?.backoffMultiplier ?? 1.3,
    maxRetries: config?.maxRetries ?? 5,
    taskType: config?.taskType ?? 'general'
  }
}

/**
 * Утилитарная функция для создания кастомной конфигурации
 */
export function createPollingConfig(
  baseInterval: number,
  maxInterval: number,
  backoffMultiplier: number = 1.5,
  maxRetries: number = 5,
  taskType: PollingConfig['taskType'] = 'general'
): PollingConfig {
  return {
    baseInterval,
    maxInterval,
    backoffMultiplier,
    maxRetries,
    taskType
  }
}