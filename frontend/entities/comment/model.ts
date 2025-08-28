import type { VKCommentResponse, CommentWithKeywords } from '@/shared/types'

export class Comment {
  id: number
  text: string
  authorId: number
  authorName: string | undefined
  publishedAt: string
  vkId: number
  postId: number
  likesCount: number
  hasAttachments: boolean
  matchedKeywordsCount: number
  isProcessed: boolean
  isViewed: boolean
  isArchived: boolean

  constructor(data: VKCommentResponse) {
    this.id = data.id
    this.text = data.text
    this.authorId = data.author_id
    this.authorName = data.author_name || undefined
    this.publishedAt = data.published_at
    this.vkId = data.vk_id
    this.postId = data.post_id
    this.likesCount = data.likes_count
    this.hasAttachments = data.has_attachments
    this.matchedKeywordsCount = data.matched_keywords_count
    this.isProcessed = data.is_processed
    this.isViewed = !!data.viewed_at
    this.isArchived = !!data.archived_at
  }

  get isOverdue(): boolean {
    try {
      const publishedDate = new Date(this.publishedAt)
      const now = new Date()
      if (isNaN(publishedDate.getTime())) {
        return false
      }
      const diffInHours =
        (now.getTime() - publishedDate.getTime()) / (1000 * 60 * 60)
      return diffInHours > 24
    } catch {
      return false
    }
  }

  get formattedPublishedAt(): string {
    try {
      const date = new Date(this.publishedAt)
      return isNaN(date.getTime())
        ? 'Неверная дата'
        : date.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          })
    } catch {
      return 'Неверная дата'
    }
  }

  get status(): 'new' | 'viewed' | 'archived' {
    if (this.isArchived) return 'archived'
    if (this.isViewed) return 'viewed'
    return 'new'
  }

  static fromAPI(data: VKCommentResponse): Comment {
    return new Comment(data)
  }

  static fromAPIWithKeywords(data: CommentWithKeywords): Comment {
    return new Comment(data)
  }
}
