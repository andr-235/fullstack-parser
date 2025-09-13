import { useState, useEffect } from 'react'

/**
 * Хук для дебаунса значения
 * @param value - значение для дебаунса
 * @param delay - задержка в миллисекундах
 * @returns дебаунсированное значение
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}
