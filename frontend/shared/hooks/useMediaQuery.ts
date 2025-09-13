import { useState, useEffect } from 'react'

/**
 * Хук для работы с медиа-запросами
 * @param query - CSS медиа-запрос
 * @returns boolean - соответствует ли запрос
 */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return

    const media = window.matchMedia(query)

    // Устанавливаем начальное значение
    setMatches(media.matches)

    // Слушаем изменения
    const handler = (event: MediaQueryListEvent) => {
      setMatches(event.matches)
    }

    // Современные браузеры
    if (media.addEventListener) {
      media.addEventListener('change', handler)
      return () => media.removeEventListener('change', handler)
    }
    // Старые браузеры
    else {
      media.addListener(handler)
      return () => media.removeListener(handler)
    }
  }, [query])

  return matches
}

// Предустановленные медиа-запросы
export const useBreakpoints = () => {
  const isMobile = useMediaQuery('(max-width: 640px)')
  const isTablet = useMediaQuery('(min-width: 641px) and (max-width: 1024px)')
  const isDesktop = useMediaQuery('(min-width: 1025px)')
  const isLargeScreen = useMediaQuery('(min-width: 1280px)')

  return {
    isMobile,
    isTablet,
    isDesktop,
    isLargeScreen,
  }
}
