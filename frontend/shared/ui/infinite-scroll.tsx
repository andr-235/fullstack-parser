'use client'

import React, { useEffect, useRef, useCallback } from 'react'
import { LoadingSpinner } from './loading-spinner'

interface InfiniteScrollProps {
  children: React.ReactNode
  hasNextPage?: boolean
  isFetchingNextPage: boolean
  fetchNextPage: () => void
  className?: string
}

export function InfiniteScroll({
  children,
  hasNextPage,
  isFetchingNextPage,
  fetchNextPage,
  className = '',
}: InfiniteScrollProps) {
  const observerRef = useRef<HTMLDivElement>(null)

  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [target] = entries
      if (target.isIntersecting && hasNextPage && !isFetchingNextPage) {
        fetchNextPage()
      }
    },
    [hasNextPage, isFetchingNextPage, fetchNextPage]
  )

  useEffect(() => {
    const element = observerRef.current
    if (!element) return

    const observer = new IntersectionObserver(handleObserver, {
      root: null,
      rootMargin: '100px',
      threshold: 0.1,
    })

    observer.observe(element)

    return () => observer.disconnect()
  }, [handleObserver])

  return (
    <div className={className}>
      {children}

      {/* Элемент для отслеживания скролла */}
      <div ref={observerRef} className="h-4" />

      {/* Индикатор загрузки */}
      {isFetchingNextPage && (
        <div className="flex justify-center py-4">
          <div className="flex items-center gap-2 text-slate-400">
            <LoadingSpinner className="h-4 w-4" />
            <span className="text-sm">Загрузка...</span>
          </div>
        </div>
      )}

      {/* Сообщение о конце списка */}
      {!hasNextPage && !isFetchingNextPage && (
        <div className="text-center py-4 text-slate-400 text-sm">
          Все группы загружены
        </div>
      )}
    </div>
  )
}
