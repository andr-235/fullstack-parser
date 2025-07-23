import type { VKCommentResponse, CommentWithKeywords } from '@/types/api'

export class Comment {
  id: number
  text: string
  authorId: number
  authorName?: string
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
    this.authorName = data.author_name
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
    const publishedDate = new Date(this.publishedAt)
    const now = new Date()
    const diffInHours =
      (now.getTime() - publishedDate.getTime()) / (1000 * 60 * 60)
    return diffInHours > 24
  }

  get formattedPublishedAt(): string {
    return new Date(this.publishedAt).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
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
