import type { KeywordResponse } from '@/types/api'

export class Keyword {
  id: number
  word: string
  category: string | undefined
  description: string | undefined
  isActive: boolean
  isCaseSensitive: boolean
  isWholeWord: boolean
  totalMatches: number

  constructor(data: KeywordResponse) {
    this.id = data.id
    this.word = data.word
    this.category = data.category
    this.description = data.description
    this.isActive = data.is_active
    this.isCaseSensitive = data.is_case_sensitive
    this.isWholeWord = data.is_whole_word
    this.totalMatches = data.total_matches
  }

  get isHighPriority(): boolean {
    return this.totalMatches > 100
  }

  get isMediumPriority(): boolean {
    return this.totalMatches > 50 && this.totalMatches <= 100
  }

  get isLowPriority(): boolean {
    return this.totalMatches <= 50
  }

  get priority(): 'high' | 'medium' | 'low' {
    if (this.isHighPriority) return 'high'
    if (this.isMediumPriority) return 'medium'
    return 'low'
  }

  get searchPattern(): RegExp {
    const escapedWord = this.word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const pattern = this.isWholeWord ? `\\b${escapedWord}\\b` : escapedWord
    return new RegExp(pattern, this.isCaseSensitive ? 'g' : 'gi')
  }

  matches(text: string): boolean {
    return this.searchPattern.test(text)
  }

  static fromAPI(data: KeywordResponse): Keyword {
    return new Keyword(data)
  }
}
