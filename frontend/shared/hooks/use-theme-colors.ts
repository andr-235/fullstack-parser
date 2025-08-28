import { useTheme } from 'next-themes'
import { useMemo } from 'react'

/**
 * Хук для получения текущей темы
 */
export function useCurrentTheme() {
  const { theme, resolvedTheme } = useTheme()

  return {
    theme: theme || 'system',
    resolvedTheme: resolvedTheme || 'light',
    isDark: resolvedTheme === 'dark',
    isLight: resolvedTheme === 'light',
    isSystem: theme === 'system',
  }
}

/**
 * Хук для получения адаптивных цветов в зависимости от темы
 */
export function useThemeColors() {
  const { isDark } = useCurrentTheme()

  return useMemo(
    () => ({
      // Фоновые цвета
      background: isDark ? 'hsl(var(--background))' : 'hsl(var(--background))',
      foreground: isDark ? 'hsl(var(--foreground))' : 'hsl(var(--foreground))',

      // Цвета карточек
      card: isDark ? 'hsl(var(--card))' : 'hsl(var(--card))',
      'card-foreground': isDark
        ? 'hsl(var(--card-foreground))'
        : 'hsl(var(--card-foreground))',

      // Цвета поповеров
      popover: isDark ? 'hsl(var(--popover))' : 'hsl(var(--popover))',
      'popover-foreground': isDark
        ? 'hsl(var(--popover-foreground))'
        : 'hsl(var(--popover-foreground))',

      // Основные цвета
      primary: isDark ? 'hsl(var(--primary))' : 'hsl(var(--primary))',
      'primary-foreground': isDark
        ? 'hsl(var(--primary-foreground))'
        : 'hsl(var(--primary-foreground))',

      // Вторичные цвета
      secondary: isDark ? 'hsl(var(--secondary))' : 'hsl(var(--secondary))',
      'secondary-foreground': isDark
        ? 'hsl(var(--secondary-foreground))'
        : 'hsl(var(--secondary-foreground))',

      // Мутация цвета
      muted: isDark ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
      'muted-foreground': isDark
        ? 'hsl(var(--muted-foreground))'
        : 'hsl(var(--muted-foreground))',

      // Акцентные цвета
      accent: isDark ? 'hsl(var(--accent))' : 'hsl(var(--accent))',
      'accent-foreground': isDark
        ? 'hsl(var(--accent-foreground))'
        : 'hsl(var(--accent-foreground))',

      // Цвета деструктивных элементов
      destructive: isDark
        ? 'hsl(var(--destructive))'
        : 'hsl(var(--destructive))',
      'destructive-foreground': isDark
        ? 'hsl(var(--destructive-foreground))'
        : 'hsl(var(--destructive-foreground))',

      // Цвета границ
      border: isDark ? 'hsl(var(--border))' : 'hsl(var(--border))',
      input: isDark ? 'hsl(var(--input))' : 'hsl(var(--input))',
      ring: isDark ? 'hsl(var(--ring))' : 'hsl(var(--ring))',

      // Градиенты для темной темы
      gradient: {
        card: isDark ? 'from-slate-800 to-slate-700' : 'from-white to-gray-50',
        header: isDark
          ? 'from-slate-900 to-slate-800'
          : 'from-gray-900 to-gray-800',
      },

      // Цвета текста
      text: {
        primary: isDark ? 'text-foreground' : 'text-foreground',
        secondary: isDark ? 'text-muted-foreground' : 'text-muted-foreground',
        inverse: isDark ? 'text-white' : 'text-black',
      },

      // Цвета для графиков
      chart: {
        grid: isDark ? '#374151' : '#e5e7eb',
        text: isDark ? '#9CA3AF' : '#6b7280',
        background: isDark ? '#1F2937' : '#ffffff',
      },
    }),
    [isDark]
  )
}

/**
 * Хук для получения CSS переменных для графиков
 */
export function useChartThemeVars() {
  const { isDark } = useCurrentTheme()

  return useMemo(
    () =>
      ({
        '--chart-grid-color': isDark ? '#374151' : '#e5e7eb',
        '--chart-text-color': isDark ? '#9CA3AF' : '#6b7280',
        '--chart-background': isDark ? '#1F2937' : '#ffffff',
        '--chart-tooltip-bg': isDark ? '#1F2937' : '#ffffff',
        '--chart-tooltip-border': isDark ? '#374151' : '#e5e7eb',
        '--chart-tooltip-text': isDark ? '#F9FAFB' : '#111827',
      }) as React.CSSProperties,
    [isDark]
  )
}

/**
 * Хук для получения адаптивных классов Tailwind
 */
export function useThemeClasses() {
  const { isDark } = useCurrentTheme()

  return useMemo(
    () => ({
      // Карточки
      card: isDark
        ? 'bg-card border-border text-card-foreground'
        : 'bg-card border-border text-card-foreground',

      // Заголовки
      header: isDark
        ? 'bg-gradient-to-r from-slate-900 to-slate-800 text-white'
        : 'bg-gradient-to-r from-white to-gray-50 text-gray-900',

      // Текст
      textPrimary: 'text-foreground',
      textSecondary: 'text-muted-foreground',
      textInverse: isDark ? 'text-white' : 'text-black',

      // Границы
      border: 'border-border',
      borderLight: 'border-border/50',

      // Фон
      background: 'bg-background',
      backgroundSecondary: 'bg-muted',

      // Ховер эффекты
      hover: isDark
        ? 'hover:bg-slate-700 hover:border-slate-600'
        : 'hover:bg-gray-50 hover:border-gray-300',

      // Фокус
      focus: 'focus:ring-ring focus:ring-offset-background',

      // Тени
      shadow: isDark
        ? 'shadow-lg shadow-black/20'
        : 'shadow-lg shadow-black/10',
    }),
    [isDark]
  )
}

/**
 * Хук для получения цвета с учетом темы
 */
export function useThemeColor(
  colorKey: keyof ReturnType<typeof useThemeColors>
) {
  const colors = useThemeColors()
  return colors[colorKey]
}

/**
 * Хук для получения адаптивных цветов для карточек и элементов
 */
export function useAdaptiveColors() {
  const { isDark } = useCurrentTheme()

  return useMemo(
    () => ({
      // Цвета для карточек
      cardBg: isDark ? 'bg-slate-800' : 'bg-white',
      cardBorder: isDark ? 'border-slate-700' : 'border-slate-200',

      // Цвета текста
      textPrimary: isDark ? 'text-slate-200' : 'text-slate-900',
      textSecondary: isDark ? 'text-slate-400' : 'text-slate-600',
      textMuted: isDark ? 'text-slate-500' : 'text-slate-500',

      // Цвета для интерактивных элементов
      hoverBg: isDark ? 'hover:bg-slate-700' : 'hover:bg-slate-100',
      focusBorder: isDark ? 'focus:border-blue-500' : 'focus:border-blue-600',
      focusRing: isDark ? 'focus:ring-blue-500' : 'focus:ring-blue-600',

      // Цвета для кнопок
      primaryButton: isDark
        ? 'bg-blue-600 hover:bg-blue-700'
        : 'bg-blue-600 hover:bg-blue-700',
      secondaryButton: isDark
        ? 'bg-slate-700 hover:bg-slate-600'
        : 'bg-slate-200 hover:bg-slate-300',
      dangerButton: isDark
        ? 'bg-red-600 hover:bg-red-700'
        : 'bg-red-600 hover:bg-red-700',

      // Цвета для статусов
      success: isDark ? 'text-green-400' : 'text-green-600',
      warning: isDark ? 'text-yellow-400' : 'text-yellow-600',
      error: isDark ? 'text-red-400' : 'text-red-600',
    }),
    [isDark]
  )
}

/**
 * Хук для создания условных классов в зависимости от темы
 */
export function useConditionalClasses(conditions: Record<string, string>) {
  const { isDark } = useCurrentTheme()

  return useMemo(() => {
    const classes: string[] = []

    Object.entries(conditions).forEach(([key, value]) => {
      if (key === 'dark' && isDark) {
        classes.push(value)
      } else if (key === 'light' && !isDark) {
        classes.push(value)
      } else if (key === 'always') {
        classes.push(value)
      }
    })

    return classes.join(' ')
  }, [conditions, isDark])
}
