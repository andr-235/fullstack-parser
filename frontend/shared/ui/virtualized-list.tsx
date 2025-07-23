'use client'

import React from 'react'
import { FixedSizeList as List } from 'react-window'
import InfiniteLoader from 'react-window-infinite-loader'

interface VirtualizedListProps<T> {
 items: T[]
 height: number
 width: number
 itemHeight: number
 itemCount: number
 hasNextPage: boolean
 isNextPageLoading: boolean
 loadNextPage: () => void
 renderItem: (props: { index: number; style: React.CSSProperties; data: T }) => React.ReactElement
 className?: string
}

export function VirtualizedList<T>({
 items,
 height,
 width,
 itemHeight,
 itemCount,
 hasNextPage,
 isNextPageLoading,
 loadNextPage,
 renderItem,
 className = '',
}: VirtualizedListProps<T>) {
 // Если есть следующая страница, увеличиваем количество элементов
 const itemCountWithNextPage = hasNextPage ? itemCount + 1 : itemCount

 // Функция для определения, загружен ли элемент
 const isItemLoaded = (index: number) => !hasNextPage || index < items.length

 // Функция для загрузки следующей страницы
 const loadMoreItems = (startIndex: number, stopIndex: number) => {
  if (!isNextPageLoading && hasNextPage) {
   loadNextPage()
  }
  return Promise.resolve()
 }

 return (
  <div className={className}>
   <InfiniteLoader
    isItemLoaded={isItemLoaded}
    itemCount={itemCountWithNextPage}
    loadMoreItems={loadMoreItems}
   >
    {({ onItemsRendered, ref }) => (
     <List
      ref={ref}
      height={height}
      width={width}
      itemCount={itemCountWithNextPage}
      itemSize={itemHeight}
      onItemsRendered={onItemsRendered}
      className="scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-slate-800"
     >
      {({ index, style }: { index: number; style: React.CSSProperties }) => {
       if (!isItemLoaded(index)) {
        return (
         <div style={style} className="flex items-center justify-center p-4">
          <div className="animate-pulse">
           <div className="h-4 bg-slate-700 rounded w-3/4 mb-2"></div>
           <div className="h-3 bg-slate-700 rounded w-1/2"></div>
          </div>
         </div>
        )
       }

       const item = items[index]
       if (item) {
        return renderItem({ index, style, data: item })
       }
       return null
      }}
     </List>
    )}
   </InfiniteLoader>
  </div>
 )
} 