export interface VKGroup {
  id: number
  name: string
  screen_name: string
  is_active: boolean
  members_count?: number
  description?: string
  photo_200?: string
  photo_url?: string
  total_comments_found: number
  last_parsed_at?: string
  max_posts_to_check?: number
  created_at: string
  updated_at: string
}

export interface GroupsFilters {
  is_active?: boolean
  active_only?: boolean
  search?: string
  page?: number
  size?: number
}

export interface GroupsResponse {
  items: VKGroup[]
  total: number
  page: number
  size: number
  total_pages: number
}

export interface CreateGroupRequest {
  group_id: number
  name?: string
  screen_name?: string
}

export interface UpdateGroupRequest {
  is_active?: boolean
  name?: string
  description?: string
}

export interface GroupStats {
  total_groups: number
  active_groups: number
  inactive_groups: number
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
}
