import { useMemo } from 'react'

/**
 * Хук для форматирования чисел в компактном виде
 * @param value - Число для форматирования
 * @param options - Опции форматирования
 * @returns Отформатированное число
 */
export function useNumberFormat(
  value: number,
  options: {
    compact?: boolean
    decimals?: number
    locale?: string
  } = {}
): string {
  const { compact = false, decimals = 0, locale = 'ru-RU' } = options

  return useMemo(() => {
    if (typeof value !== 'number' || isNaN(value)) {
      return '0'
    }

    if (compact) {
      if (value >= 1e9) {
        return `${(value / 1e9).toFixed(decimals)}B`
      }
      if (value >= 1e6) {
        return `${(value / 1e6).toFixed(decimals)}M`
      }
      if (value >= 1e3) {
        return `${(value / 1e3).toFixed(decimals)}K`
      }
    }

    return value.toLocaleString(locale, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })
  }, [value, compact, decimals, locale])
}

/**
 * Хук для форматирования процентов
 * @param value - Значение (0-1 или 0-100)
 * @param options - Опции форматирования
 * @returns Отформатированный процент
 */
export function usePercentFormat(
  value: number,
  options: {
    decimals?: number
    multiplyBy100?: boolean
    showSymbol?: boolean
  } = {}
): string {
  const { decimals = 1, multiplyBy100 = false, showSymbol = true } = options

  return useMemo(() => {
    if (typeof value !== 'number' || isNaN(value)) {
      return '0%'
    }

    const percentValue = multiplyBy100 ? value : value * 100
    const formatted = percentValue.toFixed(decimals)

    return showSymbol ? `${formatted}%` : formatted
  }, [value, decimals, multiplyBy100, showSymbol])
}

/**
 * Хук для форматирования байтов в читаемый вид
 * @param bytes - Количество байтов
 * @param options - Опции форматирования
 * @returns Отформатированный размер файла
 */
export function useBytesFormat(
  bytes: number,
  options: {
    decimals?: number
    binary?: boolean
  } = {}
): string {
  const { decimals = 2, binary = false } = options

  return useMemo(() => {
    if (bytes === 0) return '0 Bytes'

    const k = binary ? 1024 : 1000
    const sizes = binary
      ? ['Bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']
      : ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB']

    const i = Math.floor(Math.log(bytes) / Math.log(k))

    return `${(bytes / Math.pow(k, i)).toFixed(decimals)} ${sizes[i]}`
  }, [bytes, decimals, binary])
}

/**
 * Хук для форматирования денежных значений
 * @param value - Число для форматирования
 * @param options - Опции форматирования
 * @returns Отформатированная денежная сумма
 */
export function useCurrencyFormat(
  value: number,
  options: {
    currency?: string
    locale?: string
    decimals?: number
  } = {}
): string {
  const { currency = 'RUB', locale = 'ru-RU', decimals } = options

  return useMemo(() => {
    if (typeof value !== 'number' || isNaN(value)) {
      return '0 ₽'
    }

    return value.toLocaleString(locale, {
      style: 'currency',
      currency,
      minimumFractionDigits: decimals ?? 0,
      maximumFractionDigits: decimals ?? 2,
    })
  }, [value, currency, locale, decimals])
}
