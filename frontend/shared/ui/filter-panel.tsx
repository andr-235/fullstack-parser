'use client'

import * as React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Label } from '@/shared/ui'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui'
import { Checkbox } from '@/shared/ui'
import { Badge } from '@/shared/ui'
// Date components will need to be imported from react-day-picker or similar library
// import { Calendar } from 'react-day-picker'
// import { Popover, PopoverContent, PopoverTrigger } from '@/shared/ui'
import { cn } from '@/shared/lib/utils'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'
import { CalendarIcon, Filter, X, RotateCcw, ChevronDown, ChevronUp } from 'lucide-react'

export interface FilterOption {
 label: string
 value: any
}

export interface FilterField {
 /** Ключ фильтра */
 key: string
 /** Тип фильтра */
 type: 'text' | 'select' | 'multiselect' | 'date' | 'daterange' | 'number' | 'checkbox'
 /** Заголовок фильтра */
 label: string
 /** Placeholder для поля */
 placeholder?: string
 /** Опции для селекта */
 options?: FilterOption[]
 /** Значение по умолчанию */
 defaultValue?: any
 /** Можно ли очищать фильтр */
 clearable?: boolean
 /** Ширина поля */
 width?: string
}

export interface FilterPanelProps {
 /** Конфигурация фильтров */
 fields: FilterField[]
 /** Текущие значения фильтров */
 values: Record<string, any>
 /** Обработчик изменения фильтров */
 onChange: (key: string, value: any) => void
 /** Обработчик применения фильтров */
 onApply?: (filters: Record<string, any>) => void
 /** Обработчик сброса фильтров */
 onReset?: () => void
 /** Заголовок панели */
 title?: string
 /** Можно ли сворачивать панель */
 collapsible?: boolean
 /** Свернута ли панель по умолчанию */
 defaultCollapsed?: boolean
 /** Классы для стилизации */
 className?: string
 /** Действия с панелью */
 actions?: React.ReactNode
}

/**
 * Универсальный компонент панели фильтров
 * Заменяет повторяющиеся паттерны фильтрации по всему приложению
 */
export function FilterPanel({
 fields,
 values,
 onChange,
 onApply,
 onReset,
 title = 'Фильтры',
 collapsible = true,
 defaultCollapsed = false,
 className,
 actions,
}: FilterPanelProps) {
 const [isCollapsed, setIsCollapsed] = React.useState(defaultCollapsed)
 const [localValues, setLocalValues] = React.useState(values)

 // Синхронизируем локальные значения с внешними
 React.useEffect(() => {
  setLocalValues(values)
 }, [values])

 const handleValueChange = (key: string, value: any) => {
  const newValues = { ...localValues, [key]: value }
  setLocalValues(newValues)
  onChange(key, value)
 }

 const handleApply = () => {
  onApply?.(localValues)
 }

 const handleReset = () => {
  const resetValues = fields.reduce((acc, field) => {
   acc[field.key] = field.defaultValue ?? null
   return acc
  }, {} as Record<string, any>)

  setLocalValues(resetValues)
  onReset?.()

  // Сбрасываем все фильтры
  fields.forEach(field => {
   onChange(field.key, field.defaultValue ?? null)
  })
 }

 const getActiveFiltersCount = () => {
  return fields.filter(field => {
   const value = localValues[field.key]
   const defaultValue = field.defaultValue ?? null
   return value !== defaultValue && value !== null && value !== undefined && value !== ''
  }).length
 }

 const renderFilterField = (field: FilterField) => {
  const value = localValues[field.key]
  const fieldId = `filter-${field.key}`

  switch (field.type) {
   case 'text':
    return (
     <Input
      id={fieldId}
      value={value || ''}
      onChange={(e) => handleValueChange(field.key, e.target.value)}
      placeholder={field.placeholder}
      className={field.width}
     />
    )

   case 'select':
    return (
     <Select
      value={value || ''}
      onValueChange={(newValue) => handleValueChange(field.key, newValue)}
     >
      <SelectTrigger className={field.width}>
       <SelectValue placeholder={field.placeholder} />
      </SelectTrigger>
      <SelectContent>
       {field.options?.map((option) => (
        <SelectItem key={option.value} value={option.value}>
         {option.label}
        </SelectItem>
       ))}
      </SelectContent>
     </Select>
    )

   case 'multiselect':
    const selectedValues = Array.isArray(value) ? value : []
    return (
     <div className="space-y-2">
      {field.options?.map((option) => (
       <div key={option.value} className="flex items-center space-x-2">
        <Checkbox
         id={`${fieldId}-${option.value}`}
         checked={selectedValues.includes(option.value)}
         onCheckedChange={(checked) => {
          const newValues = checked
           ? [...selectedValues, option.value]
           : selectedValues.filter(v => v !== option.value)
          handleValueChange(field.key, newValues)
         }}
        />
        <Label
         htmlFor={`${fieldId}-${option.value}`}
         className="text-sm font-normal cursor-pointer"
        >
         {option.label}
        </Label>
       </div>
      ))}
     </div>
    )

   case 'date':
    return (
     <Input
      id={fieldId}
      type="date"
      value={value || ''}
      onChange={(e) => handleValueChange(field.key, e.target.value)}
      placeholder={field.placeholder}
      className={field.width}
     />
    )

   case 'daterange':
    return (
     <div className="flex gap-2">
      <Input
       type="date"
       placeholder="От"
       value={Array.isArray(value) ? value[0] || '' : ''}
       onChange={(e) =>
        handleValueChange(field.key, [
         e.target.value,
         Array.isArray(value) ? value[1] : null
        ])
       }
      />
      <Input
       type="date"
       placeholder="До"
       value={Array.isArray(value) ? value[1] || '' : ''}
       onChange={(e) =>
        handleValueChange(field.key, [
         Array.isArray(value) ? value[0] : null,
         e.target.value
        ])
       }
      />
     </div>
    )

   case 'number':
    return (
     <Input
      id={fieldId}
      type="number"
      value={value || ''}
      onChange={(e) => {
       const numValue = e.target.value ? Number(e.target.value) : null
       handleValueChange(field.key, numValue)
      }}
      placeholder={field.placeholder}
      className={field.width}
     />
    )

   case 'checkbox':
    return (
     <div className="flex items-center space-x-2">
      <Checkbox
       id={fieldId}
       checked={Boolean(value)}
       onCheckedChange={(checked) => handleValueChange(field.key, checked)}
      />
      <Label htmlFor={fieldId} className="text-sm font-normal cursor-pointer">
       {field.label}
      </Label>
     </div>
    )

   default:
    return null
  }
 }

 const activeFiltersCount = getActiveFiltersCount()

 return (
  <Card className={className}>
   <CardHeader
    className={cn(
     'pb-3',
     collapsible && 'cursor-pointer',
     'flex flex-row items-center justify-between space-y-0'
    )}
    onClick={() => collapsible && setIsCollapsed(!isCollapsed)}
   >
    <div className="flex items-center gap-2">
     <Filter className="h-5 w-5" />
     <CardTitle className="text-lg">{title}</CardTitle>
     {activeFiltersCount > 0 && (
      <Badge variant="secondary" className="ml-2">
       {activeFiltersCount}
      </Badge>
     )}
    </div>

    <div className="flex items-center gap-2">
     {actions}

     {(onApply || onReset) && (
      <div className="flex items-center gap-2">
       {onReset && (
        <Button
         variant="ghost"
         size="sm"
         onClick={(e) => {
          e.stopPropagation()
          handleReset()
         }}
         className="h-8 w-8 p-0"
        >
         <RotateCcw className="h-4 w-4" />
        </Button>
       )}

       {onApply && (
        <Button
         size="sm"
         onClick={(e) => {
          e.stopPropagation()
          handleApply()
         }}
        >
         Применить
        </Button>
       )}
      </div>
     )}

     {collapsible && (
      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
       {isCollapsed ? (
        <ChevronDown className="h-4 w-4" />
       ) : (
        <ChevronUp className="h-4 w-4" />
       )}
      </Button>
     )}
    </div>
   </CardHeader>

   {!isCollapsed && (
    <CardContent className="space-y-4">
     <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {fields.map((field) => (
       <div key={field.key} className="space-y-2">
        <Label htmlFor={`filter-${field.key}`} className="text-sm font-medium">
         {field.label}
        </Label>
        {renderFilterField(field)}
       </div>
      ))}
     </div>
    </CardContent>
   )}
  </Card>
 )
}

/**
 * Хук для управления фильтрами
 */
export function useFilters<T extends Record<string, any>>(
 initialFilters: T = {} as T,
 debounceMs: number = 300
) {
 const [filters, setFilters] = React.useState<T>(initialFilters)
 const [appliedFilters, setAppliedFilters] = React.useState<T>(initialFilters)

 const updateFilter = React.useCallback((key: keyof T, value: any) => {
  setFilters(prev => ({ ...prev, [key]: value }))
 }, [])

 const applyFilters = React.useCallback(() => {
  setAppliedFilters(filters)
 }, [filters])

 const resetFilters = React.useCallback(() => {
  setFilters(initialFilters)
  setAppliedFilters(initialFilters)
 }, [initialFilters])

 const clearFilter = React.useCallback((key: keyof T) => {
  const defaultValue = initialFilters[key]
  updateFilter(key, defaultValue)
 }, [initialFilters, updateFilter])

 const hasActiveFilters = React.useMemo(() => {
  return Object.entries(filters).some(([key, value]) => {
   const initialValue = initialFilters[key as keyof T]
   return value !== initialValue && value !== null && value !== undefined && value !== ''
  })
 }, [filters, initialFilters])

 return {
  filters,
  appliedFilters,
  updateFilter,
  applyFilters,
  resetFilters,
  clearFilter,
  hasActiveFilters,
  setFilters,
  setAppliedFilters,
 }
}
