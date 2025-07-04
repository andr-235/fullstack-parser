import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Объединяет CSS классы с поддержкой условных классов
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Форматирует число с разделителями тысяч
 */
export function formatNumber(num: number): string {
  return new Intl.NumberFormat('ru-RU').format(num)
}

/**
 * Форматирует дату в читаемый формат
 */
export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date))
}

/**
 * Форматирует длительность в секундах в читаемый формат
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds} сек`
  
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes} мин ${seconds % 60} сек`
  
  const hours = Math.floor(minutes / 60)
  return `${hours} ч ${minutes % 60} мин`
}

/**
 * Форматирует относительное время (упрощенная версия)
 */
export function formatRelativeTime(date: string | Date): string {
  const now = new Date()
  const target = new Date(date)
  const diffInMinutes = Math.floor((now.getTime() - target.getTime()) / (1000 * 60))
  
  if (diffInMinutes < 1) return 'только что'
  if (diffInMinutes < 60) return `${diffInMinutes} мин назад`
  
  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) return `${diffInHours} ч назад`
  
  const diffInDays = Math.floor(diffInHours / 24)
  return `${diffInDays} дн назад`
}

/**
 * Безопасное извлечение значения из объекта
 */
export function safeGet<T>(obj: any, path: string, defaultValue: T): T {
  try {
    return path.split('.').reduce((acc, key) => acc?.[key], obj) ?? defaultValue
  } catch {
    return defaultValue
  }
}

/**
 * Debounce функция для оптимизации
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
} 