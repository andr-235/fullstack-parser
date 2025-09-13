import { ReactNode } from 'react'

import { cn } from '@/shared/lib/utils'

export interface HighlightTextProps {
  text: string
  keywords: string[]
  className?: string
  highlightClassName?: string
  caseSensitive?: boolean
}

export const HighlightText = ({
  text,
  keywords,
  className,
  highlightClassName = 'bg-yellow-200 text-yellow-900 px-1 rounded',
  caseSensitive = false,
}: HighlightTextProps) => {
  if (!keywords.length || !text) {
    return <span className={className}>{text}</span>
  }

  const createHighlightedText = (): ReactNode[] => {
    const _normalizedText = caseSensitive ? text : text.toLowerCase()
    const normalizedKeywords = caseSensitive
      ? keywords
      : keywords.map(keyword => keyword.toLowerCase())

    // Создаем регулярное выражение для поиска всех ключевых слов
    const escapedKeywords = normalizedKeywords
      .map(keyword => keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
      .join('|')

    const regex = new RegExp(`(${escapedKeywords})`, caseSensitive ? 'g' : 'gi')
    const parts = text.split(regex)

    return parts.map((part, index) => {
      const isKeyword = normalizedKeywords.some(keyword =>
        caseSensitive ? part === keyword : part.toLowerCase() === keyword
      )

      if (isKeyword) {
        return (
          <mark key={index} className={cn(highlightClassName)}>
            {part}
          </mark>
        )
      }

      return part
    })
  }

  return <span className={className}>{createHighlightedText()}</span>
}
