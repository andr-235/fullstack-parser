export interface BaseEntity {
  id: number;
  createdAt: string;
  updatedAt: string;
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  limit: number;
  totalPages: number;
  groups?: T[];
  keywords?: T[];
  comments?: T[];
  items?: T[];
}

export interface VKGroupBase {
  screenName: string;
  name: string;
  description?: string;
  isActive: boolean;
  maxPostsToCheck: number;
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
  vkId: number;
  screenName: string;
  name: string;
  description: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  postCount: number;
}

export interface VKGroupStats {
  totalGroups: number;
  activeGroups: number;
  inactiveGroups: number;
  pendingGroups: number;
  totalMembers: number;
  totalComments: number;
  totalKeywords: number;
  parsingEnabledGroups: number;
}
