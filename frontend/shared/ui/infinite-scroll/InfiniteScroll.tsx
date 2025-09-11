import { useEffect, useRef, useCallback } from 'react'

import { cn } from '@/shared/lib/utils'

export interface InfiniteScrollProps {
 children: React.ReactNode
 hasMore: boolean
 loading: boolean
 onLoadMore: () => void
 className?: string
 threshold?: number
 rootMargin?: string
}

export const InfiniteScroll = ({
 children,
 hasMore,
 loading,
 onLoadMore,
 className,
 threshold = 0.1,
 rootMargin = '100px',
}: InfiniteScrollProps) => {
 const observerRef = useRef<IntersectionObserver | null>(null)
 const sentinelRef = useRef<HTMLDivElement | null>(null)

 const handleIntersection = useCallback(
  (entries: IntersectionObserverEntry[]) => {
   const [entry] = entries
   if (entry?.isIntersecting && hasMore && !loading) {
    onLoadMore()
   }
  },
  [hasMore, loading, onLoadMore]
 )

 useEffect(() => {
  if (observerRef.current) {
   observerRef.current.disconnect()
  }

  if (sentinelRef.current) {
   observerRef.current = new IntersectionObserver(handleIntersection, {
    threshold,
    rootMargin,
   })
   observerRef.current.observe(sentinelRef.current)
  }

  return () => {
   if (observerRef.current) {
    observerRef.current.disconnect()
   }
  }
 }, [handleIntersection, threshold, rootMargin])

 return (
  <div className={cn('space-y-4', className)}>
   {children}

   {/* Sentinel element for intersection observer */}
   <div ref={sentinelRef} className="h-4" />

   {/* Loading indicator */}
   {loading && (
    <div className="flex justify-center py-4">
     <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
    </div>
   )}

   {/* End of list indicator */}
   {!hasMore && !loading && (
    <div className="text-center py-4 text-muted-foreground">
     Все комментарии загружены
    </div>
   )}
  </div>
 )
}
