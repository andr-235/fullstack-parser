import type { VKCommentResponse, KeywordResponse } from '@/types/api'

export interface CommentProcessingResult {
  comment: any // Будет типизировано через shared
  matchedKeywords: any[] // Будет типизировано через shared
  processingTime: number
  success: boolean
  error?: string
}

export class CommentProcessingService {
  private keywords: any[] = [] // Будет типизировано через shared

  constructor(keywords: KeywordResponse[]) {
    this.keywords = keywords
  }

  async processComment(
    commentData: VKCommentResponse
  ): Promise<CommentProcessingResult> {
    const startTime = Date.now()

    try {
      const comment = commentData // Упрощенная версия без модели
      const matchedKeywords = this.findMatchingKeywords(comment.text)

      return {
        comment,
        matchedKeywords,
        processingTime: Date.now() - startTime,
        success: true,
      }
    } catch (error) {
      return {
        comment: commentData,
        matchedKeywords: [],
        processingTime: Date.now() - startTime,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      }
    }
  }

  private findMatchingKeywords(text: string): any[] {
    return this.keywords.filter((keyword) => {
      const escapedWord = keyword.word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      const pattern = keyword.is_whole_word
        ? `\\b${escapedWord}\\b`
        : escapedWord
      const regex = new RegExp(pattern, keyword.is_case_sensitive ? 'g' : 'gi')
      return regex.test(text)
    })
  }

  async processBatch(
    comments: VKCommentResponse[]
  ): Promise<CommentProcessingResult[]> {
    const results: CommentProcessingResult[] = []

    for (const comment of comments) {
      const result = await this.processComment(comment)
      results.push(result)
    }

    return results
  }
}
