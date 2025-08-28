'use client'

import * as React from 'react'
import {
 Table,
 TableBody,
 TableCell,
 TableHead,
 TableHeader,
 TableRow,
} from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Checkbox } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { LoadingState, EmptyState } from '@/shared/ui'
import { cn } from '@/shared/lib/utils'
import { useNumberFormat } from '@/shared/hooks'
import {
 ChevronUp,
 ChevronDown,
 ChevronsUpDown,
 ArrowUpDown,
 Search,
 Filter,
 Download,
 MoreHorizontal,
} from 'lucide-react'

export interface Column<T = any> {
 /** Ключ колонки для доступа к данным */
 key: keyof T
 /** Заголовок колонки */
 title: string
 /** Ширина колонки */
 width?: string | number
 /** Выравнивание содержимого */
 align?: 'left' | 'center' | 'right'
 /** Можно ли сортировать по этой колонке */
 sortable?: boolean
 /** Кастомный рендер для ячейки */
 render?: (value: any, record: T, index: number) => React.ReactNode
 /** Кастомный рендер для заголовка */
 headerRender?: () => React.ReactNode
 /** Фильтр для колонки */
 filterable?: boolean
 /** Тип данных для фильтрации */
 filterType?: 'text' | 'select' | 'date' | 'number'
 /** Опции для селект фильтра */
 filterOptions?: Array<{ label: string; value: any }>
}

export interface DataTableProps<T = any> {
 /** Данные для таблицы */
 data: T[]
 /** Конфигурация колонок */
 columns: Column<T>[]
 /** Загрузка данных */
 loading?: boolean
 /** Выбор строк */
 rowSelection?: {
  selectedRowKeys: string[] | number[]
  onChange: (selectedRowKeys: string[] | number[], selectedRows: T[]) => void
  getRowKey?: (record: T) => string | number
 }
 /** Сортировка */
 sortConfig?: {
  key: keyof T
  direction: 'asc' | 'desc'
  onSort: (key: keyof T, direction: 'asc' | 'desc') => void
 }
 /** Пагинация */
 pagination?: {
  current: number
  pageSize: number
  total: number
  onChange: (page: number, pageSize: number) => void
  showSizeChanger?: boolean
  pageSizeOptions?: number[]
 }
 /** Пустое состояние */
 emptyText?: string
 /** Размер таблицы */
 size?: 'small' | 'medium' | 'large'
 /** Границы таблицы */
 bordered?: boolean
 /** Полосатые строки */
 striped?: boolean
 /** Классы для стилизации */
 className?: string
 /** Действия с таблицей */
 actions?: React.ReactNode
}

/**
 * Универсальный компонент таблицы с сортировкой, фильтрацией и пагинацией
 * Заменяет повторяющиеся паттерны таблиц по всему приложению
 */
export function DataTable<T extends Record<string, any>>({
 data,
 columns,
 loading = false,
 rowSelection,
 sortConfig,
 pagination,
 emptyText = 'Нет данных',
 size = 'medium',
 bordered = false,
 striped = false,
 className,
 actions,
}: DataTableProps<T>) {
 const formatNumber = useNumberFormat

 const handleSort = (column: Column<T>) => {
  if (!column.sortable || !sortConfig) return

  const newDirection =
   sortConfig.key === column.key && sortConfig.direction === 'asc'
    ? 'desc'
    : 'asc'

  sortConfig.onSort(column.key, newDirection)
 }

 const getSortIcon = (column: Column<T>) => {
  if (!column.sortable) return null

  if (sortConfig?.key !== column.key) {
   return <ArrowUpDown className="h-4 w-4 ml-1" />
  }

  return sortConfig.direction === 'asc'
   ? <ChevronUp className="h-4 w-4 ml-1" />
   : <ChevronDown className="h-4 w-4 ml-1" />
 }

 const getRowKey = (record: T, index: number) => {
  return rowSelection?.getRowKey?.(record) ?? index
 }

 const isRowSelected = (key: string | number) => {
  return rowSelection?.selectedRowKeys?.includes(key as never) ?? false
 }

 const handleRowSelect = (key: string | number, checked: boolean) => {
  if (!rowSelection) return

  const newSelectedKeys = checked
   ? [...rowSelection.selectedRowKeys, key]
   : rowSelection.selectedRowKeys.filter(k => k !== key)

  const selectedRows = data.filter((_, index) =>
   newSelectedKeys.includes(getRowKey(_, index))
  )

  rowSelection.onChange(newSelectedKeys as string[] | number[], selectedRows)
 }

 const handleSelectAll = (checked: boolean) => {
  if (!rowSelection) return

  const allKeys = data.map((_, index) => getRowKey(_, index))
  const newSelectedKeys = checked ? allKeys : []
  const selectedRows = checked ? data : []

  rowSelection.onChange(newSelectedKeys as string[] | number[], selectedRows)
 }

 const sizeClasses = {
  small: 'text-sm',
  medium: 'text-sm',
  large: 'text-base',
 }

 const allSelected = data.length > 0 && data.every((_, index) =>
  isRowSelected(getRowKey(_, index))
 )
 const someSelected = data.some((_, index) =>
  isRowSelected(getRowKey(_, index))
 )

 if (loading) {
  return <LoadingState />
 }

 return (
  <div className={cn('space-y-4', className)}>
   {/* Панель действий */}
   {(actions || rowSelection) && (
    <div className="flex items-center justify-between">
     <div className="flex items-center gap-2">
      {rowSelection && (
       <div className="text-sm text-muted-foreground">
        Выбрано: {rowSelection.selectedRowKeys.length} из {data.length}
       </div>
      )}
     </div>

     <div className="flex items-center gap-2">
      {actions}
     </div>
    </div>
   )}

   {/* Таблица */}
   <div className={cn(
    'border rounded-lg overflow-hidden',
    bordered && 'border-border',
    !bordered && 'border-0'
   )}>
    <Table>
     <TableHeader>
      <TableRow>
       {rowSelection && (
        <TableHead className="w-12">
         <Checkbox
          checked={allSelected}
          ref={(el) => {
           if (el) (el as HTMLInputElement).indeterminate = someSelected && !allSelected
          }}
          onCheckedChange={handleSelectAll}
         />
        </TableHead>
       )}

       {columns.map((column) => (
        <TableHead
         key={String(column.key)}
         className={cn(
          sizeClasses[size],
          column.align && `text-${column.align}`,
          column.sortable && 'cursor-pointer select-none hover:bg-muted/50',
          column.width && `w-[${column.width}]`
         )}
         onClick={() => column.sortable && handleSort(column)}
        >
         <div className="flex items-center">
          {column.headerRender ? column.headerRender() : column.title}
          {getSortIcon(column)}
         </div>
        </TableHead>
       ))}
      </TableRow>
     </TableHeader>

     <TableBody>
      {data.length === 0 ? (
       <TableRow>
        <TableCell
         colSpan={columns.length + (rowSelection ? 1 : 0)}
         className="h-24"
        >
         <EmptyState
          title={emptyText}
          description="Попробуйте изменить фильтры или добавить данные"
          fullHeight={false}
         />
        </TableCell>
       </TableRow>
      ) : (
       data.map((record, index) => {
        const rowKey = getRowKey(record, index)
        return (
         <TableRow
          key={rowKey}
          className={cn(
           striped && index % 2 === 1 && 'bg-muted/30',
           isRowSelected(rowKey) && 'bg-primary/10'
          )}
         >
          {rowSelection && (
           <TableCell>
            <Checkbox
             checked={isRowSelected(rowKey)}
             onCheckedChange={(checked) =>
              handleRowSelect(rowKey, checked as boolean)
             }
            />
           </TableCell>
          )}

          {columns.map((column) => {
           const value = record[column.key]
           const cellContent = column.render
            ? column.render(value, record, index)
            : String(value ?? '')

           return (
            <TableCell
             key={String(column.key)}
             className={cn(
              sizeClasses[size],
              column.align && `text-${column.align}`
             )}
            >
             {cellContent}
            </TableCell>
           )
          })}
         </TableRow>
        )
       })
      )}
     </TableBody>
    </Table>
   </div>

   {/* Пагинация */}
   {pagination && data.length > 0 && (
    <div className="flex items-center justify-between">
     <div className="text-sm text-muted-foreground">
      Показано {((pagination.current - 1) * pagination.pageSize) + 1} -{' '}
      {Math.min(pagination.current * pagination.pageSize, pagination.total)} из{' '}
      {pagination.total} записей
     </div>

     <div className="flex items-center gap-2">
      <Button
       variant="outline"
       size="sm"
       onClick={() => pagination.onChange(pagination.current - 1, pagination.pageSize)}
       disabled={pagination.current <= 1}
      >
       Назад
      </Button>

      <span className="text-sm">
       Страница {pagination.current} из{' '}
       {Math.ceil(pagination.total / pagination.pageSize)}
      </span>

      <Button
       variant="outline"
       size="sm"
       onClick={() => pagination.onChange(pagination.current + 1, pagination.pageSize)}
       disabled={pagination.current >= Math.ceil(pagination.total / pagination.pageSize)}
      >
       Далее
      </Button>
     </div>
    </div>
   )}
  </div>
 )
}

/**
 * Компонент для быстрого создания простой таблицы
 */
interface SimpleDataTableProps<T = any> {
 data: T[]
 loading?: boolean
 emptyText?: string
 className?: string
}

export function SimpleDataTable<T extends Record<string, any>>({
 data,
 loading,
 emptyText,
 className,
}: SimpleDataTableProps<T>) {
 // Автоматически генерируем колонки из данных
 const columns = React.useMemo(() => {
  if (data.length === 0) return []

  const firstItem = data[0]
  if (!firstItem) return []

  const keys = Object.keys(firstItem)
  return keys.map(key => ({
   key: key as keyof T,
   title: key.charAt(0).toUpperCase() + key.slice(1),
   sortable: true,
  }))
 }, [data])

 return (
  <DataTable
   data={data}
   columns={columns}
   loading={loading ?? false}
   emptyText={emptyText ?? 'Нет данных'}
   className={className ?? ''}
  />
 )
}
