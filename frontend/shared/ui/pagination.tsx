'use client'

import { ChevronLeft, ChevronRight, MoreHorizontal } from 'lucide-react'

import { cn } from '@/shared/lib'

import { Button } from './button'

interface PaginationProps {
 currentPage: number
 totalPages: number
 totalItems: number
 itemsPerPage: number
 onPageChange: (page: number) => void
 className?: string
}

export function Pagination({
 currentPage,
 totalPages,
 totalItems,
 itemsPerPage,
 onPageChange,
 className,
}: PaginationProps) {
 const startItem = (currentPage - 1) * itemsPerPage + 1
 const endItem = Math.min(currentPage * itemsPerPage, totalItems)

 const getVisiblePages = () => {
  const delta = 2
  const range = []
  const rangeWithDots = []

  for (
   let i = Math.max(2, currentPage - delta);
   i <= Math.min(totalPages - 1, currentPage + delta);
   i++
  ) {
   range.push(i)
  }

  if (currentPage - delta > 2) {
   rangeWithDots.push(1, '...')
  } else {
   rangeWithDots.push(1)
  }

  rangeWithDots.push(...range)

  if (currentPage + delta < totalPages - 1) {
   rangeWithDots.push('...', totalPages)
  } else if (totalPages > 1) {
   rangeWithDots.push(totalPages)
  }

  return rangeWithDots
 }

 if (totalPages <= 1) {
  return null
 }

 return (
  <div className={cn('flex items-center justify-between', className)}>
   {/* Info */}
   <div className="text-sm text-muted-foreground">
    Показано {startItem}-{endItem} из {totalItems.toLocaleString()} записей
   </div>

   {/* Pagination Controls */}
   <div className="flex items-center space-x-2">
    {/* Previous Button */}
    <Button
     variant="outline"
     size="sm"
     onClick={() => onPageChange(currentPage - 1)}
     disabled={currentPage <= 1}
     className="h-8 w-8 p-0"
    >
     <ChevronLeft className="h-4 w-4" />
    </Button>

    {/* Page Numbers */}
    <div className="flex items-center space-x-1">
     {getVisiblePages().map((page, index) => {
      if (page === '...') {
       return (
        <div
         key={`dots-${index}`}
         className="flex h-8 w-8 items-center justify-center"
        >
         <MoreHorizontal className="h-4 w-4" />
        </div>
       )
      }

      const pageNumber = page as number
      const isCurrentPage = pageNumber === currentPage

      return (
       <Button
        key={pageNumber}
        variant={isCurrentPage ? 'default' : 'outline'}
        size="sm"
        onClick={() => onPageChange(pageNumber)}
        className="h-8 w-8 p-0"
       >
        {pageNumber}
       </Button>
      )
     })}
    </div>

    {/* Next Button */}
    <Button
     variant="outline"
     size="sm"
     onClick={() => onPageChange(currentPage + 1)}
     disabled={currentPage >= totalPages}
     className="h-8 w-8 p-0"
    >
     <ChevronRight className="h-4 w-4" />
    </Button>
   </div>
  </div>
 )
}

interface PaginationInfoProps {
 currentPage: number
 totalPages: number
 totalItems: number
 itemsPerPage: number
 className?: string
}

export function PaginationInfo({
 currentPage,
 totalPages,
 totalItems,
 itemsPerPage,
 className,
}: PaginationInfoProps) {
 const startItem = (currentPage - 1) * itemsPerPage + 1
 const endItem = Math.min(currentPage * itemsPerPage, totalItems)

 return (
  <div className={cn('text-sm text-muted-foreground', className)}>
   Страница {currentPage} из {totalPages} • Показано {startItem}-{endItem} из{' '}
   {totalItems.toLocaleString()} записей
  </div>
 )
}
