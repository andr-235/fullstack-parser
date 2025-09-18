export interface Group {
  id: number;
  vk_id: number;
  name: string;
  screen_name: string;
  description?: string;
  is_active: boolean;
  members_count?: number;
  total_comments_found: number;
  last_parsed_at?: string;
  max_posts_to_check: number;
  photo_url?: string;
  created_at: string;
  updated_at: string;
}

// Alias for Group to match VK API naming
export type VKGroup = Group;

export interface GroupsResponse {
  groups: Group[];
  total: number;
  page: number;
  size: number;
}

export interface CreateGroupRequest {
  vk_id: number;
  name: string;
  screen_name: string;
  description?: string;
  members_count?: number;
  photo_url?: string;
  max_posts_to_check?: number;
}

export interface GroupsFilters {
  search?: string;
  active_only?: boolean;
  is_active?: boolean;
  has_monitoring?: boolean;
  min_members?: number;
  max_members?: number;
  size?: number;
  page?: number;
}

export interface UpdateGroupRequest {
  name?: string;
  description?: string;
  is_active?: boolean;
  max_posts_to_check?: number;
}

export interface GroupStats {
  id: number;
  total_comments: number;
  parsed_posts: number;
  last_parsed_at?: string;
  parsing_status: 'idle' | 'running' | 'completed' | 'error';
}

export interface GroupsStats {
  total_groups: number;
  active_groups: number;
  total_comments: number;
  parsed_posts: number;
  last_updated: string;
}

export interface GroupBulkAction {
  action: 'activate' | 'deactivate' | 'delete';
  group_ids: number[];
}

export interface GroupBulkResponse {
  success: boolean;
  processed: number;
  failed: number;
  errors?: string[];
}

export interface UploadGroupsResponse {
  success: boolean;
  uploaded: number;
  failed: number;
  task_id: string;
  errors?: string[];
}

export interface UploadProgress {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  total: number;
  processed: number;
  errors?: string[];
}