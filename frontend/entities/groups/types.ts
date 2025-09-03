export interface VKGroup {
  id: number
  vk_id: number
  name: string
  screen_name: string
  is_active: boolean
  description?: string
  members_count: number
  total_posts_parsed: number
  total_comments_found: number
  last_parsed_at?: string
  photo_url?: string
  is_closed: boolean
  max_posts_to_check: number
  created_at: string
  updated_at: string
}

export interface GroupsFilters {
  is_active?: boolean
  active_only?: boolean
  search?: string
  has_monitoring?: boolean
  min_members?: number
  max_members?: number
  page?: number
  size?: number
}

export interface GroupsResponse {
  items: VKGroup[]
  total: number
  page: number
  size: number
  pages: number
}

export interface CreateGroupRequest {
  vk_id: number
  name: string
  screen_name: string
  description?: string
}

export interface UpdateGroupRequest {
  name?: string
  screen_name?: string
  description?: string
  is_active?: boolean
  max_posts_to_check?: number
}

export interface GroupStats {
  id: number
  vk_id: number
  name: string
  total_comments: number
  active_comments: number
  parsed_posts_count: number
  avg_comments_per_post: number
  last_activity?: string
}

export interface GroupsStats {
  total_groups: number
  active_groups: number
  total_comments: number
  total_parsed_posts: number
  avg_comments_per_group: number
}

export interface GroupBulkAction {
  group_ids: number[]
  action: string
}

export interface GroupBulkResponse {
  success_count: number
  error_count: number
  errors: Array<Record<string, unknown>>
}

export interface UploadGroupsResponse {
  success: number
  failed: number
  errors: string[]
}

export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
  status?: string
  progress?: number
  current_group?: string
  total_groups?: number
  processed_groups?: number
  created?: number
  skipped?: number
  errors?: string[]
}
