'use client'

import * as React from 'react'
import { Input } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { cn } from '@/shared/lib/utils'
import { useDebounce } from '@/shared/hooks'
import { Search, X, Loader2 } from 'lucide-react'

export interface SearchInputProps {
 /** Значение поиска */
 value: string
 /** Обработчик изменения значения */
 onChange: (value: string) => void
 /** Placeholder для поля поиска */
 placeholder?: string
 /** Задержка debounce в мс */
 debounceMs?: number
 /** Показывать ли кнопку очистки */
 showClearButton?: boolean
 /** Состояние загрузки */
 isLoading?: boolean
 /** Отключено ли поле */
 disabled?: boolean
 /** Размер поля */
 size?: 'sm' | 'md' | 'lg'
 /** Дополнительные классы */
 className?: string
 /** Автофокус при монтировании */
 autoFocus?: boolean
 /** Максимальная длина текста */
 maxLength?: number
 /** Обработчик фокуса */
 onFocus?: () => void
 /** Обработчик потери фокуса */
 onBlur?: () => void
 /** Обработчик нажатия клавиши */
 onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void
 /** Обработчик нажатия Enter */
 onSearch?: (value: string) => void
}

/**
 * Универсальный компонент поля поиска с debounce и дополнительными возможностями
 * Заменяет повторяющиеся паттерны поиска по всему приложению
 */
export function SearchInput({
 value,
 onChange,
 placeholder = 'Поиск...',
 debounceMs = 300,
 showClearButton = true,
 isLoading = false,
 disabled = false,
 size = 'md',
 className,
 autoFocus = false,
 maxLength,
 onFocus,
 onBlur,
 onKeyDown,
 onSearch,
}: SearchInputProps) {
 const [internalValue, setInternalValue] = React.useState(value)
 const debouncedValue = useDebounce(internalValue, debounceMs)

 // Синхронизируем внутреннее значение с внешним
 React.useEffect(() => {
  setInternalValue(value)
 }, [value])

 // Применяем debounced значение
 React.useEffect(() => {
  if (debouncedValue !== value) {
   onChange(debouncedValue)
  }
 }, [debouncedValue, onChange, value])

 const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const newValue = e.target.value
  setInternalValue(newValue)
 }

 const handleClear = () => {
  setInternalValue('')
  onChange('')
 }

 const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
  // Call external onKeyDown first
  if (onKeyDown) {
   onKeyDown(e)
  }

  // Internal key handling (only if not prevented by external handler)
  if (!e.defaultPrevented) {
   if (e.key === 'Enter' && onSearch) {
    onSearch(internalValue)
   } else if (e.key === 'Escape' && showClearButton) {
    handleClear()
   }
  }
 }

 const sizeClasses = {
  sm: 'h-8 text-sm',
  md: 'h-10',
  lg: 'h-12 text-lg',
 }

 const iconSizes = {
  sm: 'h-3 w-3',
  md: 'h-4 w-4',
  lg: 'h-5 w-5',
 }

 return (
  <div className={cn('relative flex items-center', className)}>
   <div className="absolute left-3 flex items-center pointer-events-none">
    {isLoading ? (
     <Loader2 className={cn('animate-spin', iconSizes[size])} />
    ) : (
     <Search className={iconSizes[size]} />
    )}
   </div>

   <Input
    type="text"
    value={internalValue}
    onChange={handleChange}
    onKeyDown={handleKeyDown}
    onFocus={onFocus}
    onBlur={onBlur}
    placeholder={placeholder}
    disabled={disabled || isLoading}
    maxLength={maxLength}
    autoFocus={autoFocus}
    className={cn(
     'pl-10 pr-10',
     sizeClasses[size],
     disabled && 'opacity-50 cursor-not-allowed'
    )}
   />

   {showClearButton && internalValue && !disabled && (
    <Button
     type="button"
     variant="ghost"
     size="icon"
     onClick={handleClear}
     className={cn(
      'absolute right-1 h-8 w-8',
      size === 'sm' && 'h-6 w-6',
      size === 'lg' && 'h-10 w-10'
     )}
    >
     <X className={iconSizes[size]} />
     <span className="sr-only">Очистить поиск</span>
    </Button>
   )}
  </div>
 )
}

/**
 * Компонент расширенного поиска с фильтрами
 */
interface AdvancedSearchInputProps extends Omit<SearchInputProps, 'onSearch'> {
 /** Дополнительные фильтры */
 filters?: React.ReactNode
 /** Показывать ли расширенные фильтры */
 showFilters?: boolean
 /** Обработчик переключения фильтров */
 onToggleFilters?: () => void
 /** Обработчик поиска */
 onSearch?: (query: string, filters?: any) => void
}

export function AdvancedSearchInput({
 filters,
 showFilters = false,
 onToggleFilters,
 onSearch,
 ...props
}: AdvancedSearchInputProps) {
 const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
  if (e.key === 'Enter' && onSearch) {
   onSearch(props.value)
  }
 }

 const handleSearch = (value: string) => {
  if (onSearch) {
   onSearch(value)
  }
 }

 return (
  <div className="space-y-4">
   <div className="flex gap-2">
    <div className="flex-1">
     <SearchInput
      {...props}
      onKeyDown={handleKeyDown}
      onSearch={handleSearch}
     />
    </div>

    {filters && (
     <Button
      type="button"
      variant="outline"
      onClick={onToggleFilters}
      className={cn(
       'shrink-0',
       showFilters && 'bg-primary text-primary-foreground'
      )}
     >
      <Search className="h-4 w-4 mr-2" />
      Фильтры
     </Button>
    )}
   </div>

   {showFilters && filters && (
    <div className="p-4 border rounded-lg bg-muted/30">
     {filters}
    </div>
   )}
  </div>
 )
}

/**
 * Хук для управления поиском с debounce
 */
export function useSearch(initialValue = '', debounceMs = 300) {
 const [query, setQuery] = React.useState(initialValue)
 const [isSearching, setIsSearching] = React.useState(false)
 const debouncedQuery = useDebounce(query, debounceMs)

 const handleSearch = React.useCallback((newQuery: string) => {
  setQuery(newQuery)
  if (newQuery !== query) {
   setIsSearching(true)
  }
 }, [query])

 const clearSearch = React.useCallback(() => {
  setQuery('')
  setIsSearching(false)
 }, [])

 // Останавливаем индикатор поиска после изменения debounced значения
 React.useEffect(() => {
  if (isSearching && debouncedQuery === query) {
   setIsSearching(false)
  }
 }, [debouncedQuery, query, isSearching])

 return {
  query: debouncedQuery,
  rawQuery: query,
  isSearching,
  setQuery: handleSearch,
  clearSearch,
 }
}
