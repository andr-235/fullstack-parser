export interface BaseEntity {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  size: number;
  items: T[];
}

export interface VKGroupBase {
  screen_name: string;
  name: string;
  description?: string;
  is_active: boolean;
  max_posts_to_check: number;
}

export interface VKGroupCreate {
  name: string;
  screen_name: string;
  description?: string;
  category?: string;
  parsing_enabled?: boolean;
}

export interface VKGroupUpdate {
  name?: string;
  description?: string;
  category?: string;
  parsing_enabled?: boolean;
  status?: 'active' | 'inactive' | 'pending';
}

export interface VKGroupResponse {
  id: number;
  name: string;
  screen_name: string;
  description: string;
  members_count: number;
  is_closed: boolean;
  type: string;
  photo_100: string;
  photo_200: string;
  status: 'active' | 'inactive' | 'pending';
  category: string;
  created_at: string;
  updated_at: string;
  last_parsed_at?: string;
  parsing_enabled: boolean;
  keywords_count: number;
  comments_count: number;
}

export interface VKGroupStats {
  total_groups: number;
  active_groups: number;
  inactive_groups: number;
  pending_groups: number;
  total_members: number;
  total_comments: number;
  total_keywords: number;
  parsing_enabled_groups: number;
}
