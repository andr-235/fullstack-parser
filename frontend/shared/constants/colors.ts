/**
 * Общие цветовые константы для поддержания единообразия в приложении
 * Используются для графиков, иконок и других элементов UI
 */

export const CHART_COLORS = [
  '#3B82F6', // blue-500
  '#10B981', // emerald-500
  '#F59E0B', // amber-500
  '#EF4444', // red-500
  '#8B5CF6', // violet-500
  '#06B6D4', // cyan-500
  '#84CC16', // lime-500
  '#F97316', // orange-500
] as const

export const STATUS_COLORS = {
  success: 'text-green-400',
  warning: 'text-yellow-400',
  error: 'text-red-400',
  info: 'text-blue-400',
  neutral: 'text-gray-400',
} as const

export const BADGE_VARIANTS = {
  success: 'bg-green-900 text-green-300 border-green-700',
  warning: 'bg-yellow-900 text-yellow-300 border-yellow-700',
  error: 'bg-red-900 text-red-300 border-red-700',
  info: 'bg-blue-900 text-blue-300 border-blue-700',
  neutral: 'bg-gray-900 text-gray-300 border-gray-700',
} as const

export const ICON_BACKGROUND_COLORS = {
  blue: 'bg-blue-500',
  green: 'bg-green-500',
  yellow: 'bg-yellow-500',
  red: 'bg-red-500',
  purple: 'bg-purple-500',
  gray: 'bg-gray-500',
  cyan: 'bg-cyan-500',
  orange: 'bg-orange-500',
} as const

/**
 * Получить цвет из палитры по индексу
 */
export function getChartColor(index: number): string {
  return CHART_COLORS[index % CHART_COLORS.length]!
}

/**
 * Получить контрастный цвет текста для фона
 */
export function getContrastTextColor(backgroundColor: string): string {
  // Простая логика определения контрастного цвета
  const color = backgroundColor.replace('bg-', '').replace('-500', '')
  const lightColors = ['yellow', 'lime', 'cyan', 'orange', 'amber']
  return lightColors.includes(color) ? 'text-black' : 'text-white'
}

/**
 * Цвета для карточек статистики
 */
export const STATS_COLORS = [
  'from-blue-800 to-blue-700',
  'from-green-800 to-green-700',
  'from-purple-800 to-purple-700',
  'from-red-800 to-red-700',
  'from-yellow-800 to-yellow-700',
] as const

/**
 * Цвета для иконок в карточках статистики
 */
export const STATS_ICON_COLORS = [
  'text-blue-400',
  'text-green-400',
  'text-purple-400',
  'text-red-400',
  'text-yellow-400',
] as const
