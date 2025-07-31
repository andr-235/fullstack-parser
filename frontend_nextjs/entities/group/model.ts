import type { VKGroupResponse } from '@/types/api'

export class Group {
  id: number
  vkId: number
  screenName: string
  name: string
  description: string | undefined
  isActive: boolean
  maxPostsToCheck: number
  lastParsedAt: string | undefined
  totalPostsParsed: number
  totalCommentsFound: number
  membersCount: number | undefined
  isClosed: boolean
  photoUrl: string | undefined

  constructor(data: VKGroupResponse) {
    this.id = data.id
    this.vkId = data.vk_id
    this.screenName = data.screen_name
    this.name = data.name
    this.description = data.description
    this.isActive = data.is_active
    this.maxPostsToCheck = data.max_posts_to_check
    this.lastParsedAt = data.last_parsed_at
    this.totalPostsParsed = data.total_posts_parsed
    this.totalCommentsFound = data.total_comments_found
    this.membersCount = data.members_count
    this.isClosed = data.is_closed
    this.photoUrl = data.photo_url
  }

  get isRecentlyActive(): boolean {
    if (!this.lastParsedAt) return false
    const lastParsed = new Date(this.lastParsedAt)
    const now = new Date()
    const diffInHours =
      (now.getTime() - lastParsed.getTime()) / (1000 * 60 * 60)
    return diffInHours < 24
  }

  get formattedLastParsedAt(): string {
    if (!this.lastParsedAt) return 'Никогда'
    return new Date(this.lastParsedAt).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  get vkUrl(): string {
    return `https://vk.com/${this.screenName}`
  }

  get status(): 'active' | 'inactive' | 'closed' {
    if (this.isClosed) return 'closed'
    if (this.isActive) return 'active'
    return 'inactive'
  }

  static fromAPI(data: VKGroupResponse): Group {
    return new Group(data)
  }
}
