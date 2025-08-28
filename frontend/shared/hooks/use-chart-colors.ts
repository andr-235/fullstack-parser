import { useMemo } from 'react'
import { CHART_COLORS, getChartColor } from '@/shared/constants'

/**
 * Хук для получения цветовой схемы графиков
 * @param count - Количество цветов
 * @param colors - Пользовательские цвета (опционально)
 * @returns Массив цветов для графиков
 */
export function useChartColors(count: number, colors?: string[]): string[] {
  return useMemo(() => {
    if (colors && colors.length > 0) {
      return colors.slice(0, count)
    }

    return Array.from({ length: count }, (_, index) => getChartColor(index))
  }, [count, colors])
}

/**
 * Хук для получения цвета по индексу
 * @param index - Индекс цвета
 * @param colors - Пользовательские цвета (опционально)
 * @returns Цвет для данного индекса
 */
export function useChartColor(index: number, colors?: string[]): string {
  return useMemo(() => {
    if (colors && colors.length > index) {
      const color = colors[index]
      if (color) return color
    }

    return getChartColor(index)
  }, [index, colors])
}

/**
 * Хук для создания цветовой палитры с прозрачностью
 * @param baseColors - Базовые цвета
 * @param opacity - Уровень прозрачности (0-1)
 * @returns Массив цветов с прозрачностью
 */
export function useChartColorsWithOpacity(
  baseColors: string[],
  opacity: number = 0.3
): string[] {
  return useMemo(() => {
    return baseColors.map((color) => {
      // Преобразуем hex в rgb с прозрачностью
      const hex = color.replace('#', '')
      const r = parseInt(hex.substr(0, 2), 16)
      const g = parseInt(hex.substr(2, 2), 16)
      const b = parseInt(hex.substr(4, 2), 16)

      return `rgba(${r}, ${g}, ${b}, ${opacity})`
    })
  }, [baseColors, opacity])
}
