export interface VkGroup {
  id: number;
  name: string;
  screen_name: string;
  type: 'group' | 'page' | 'event';
  is_closed: 0 | 1 | 2;
  photo_50?: string;
  photo_100?: string;
  photo_200?: string;
  description?: string;
  members_count?: number;
}

export interface VkPost {
  id: number;
  owner_id: number;
  from_id: number;
  date: number;
  text: string;
  comments?: {
    count: number;
    can_post: 0 | 1;
  };
  likes?: {
    count: number;
    user_likes: 0 | 1;
  };
  reposts?: {
    count: number;
    user_reposted: 0 | 1;
  };
  views?: {
    count: number;
  };
  attachments?: VkAttachment[];
}

export interface VkComment {
  id: number;
  from_id: number;
  date: number;
  text: string;
  reply_to_user?: number;
  reply_to_comment?: number;
  likes?: {
    count: number;
    user_likes: 0 | 1;
  };
  thread?: {
    count: number;
    items?: VkComment[];
    can_post: boolean;
  };
  attachments?: VkAttachment[];
}

export interface VkAttachment {
  type: 'photo' | 'video' | 'audio' | 'doc' | 'link' | 'note' | 'poll' | 'page' | 'album' | 'photos_list' | 'market_album' | 'market' | 'wall' | 'wall_reply' | 'sticker' | 'gift';
  photo?: VkPhoto;
  video?: VkVideo;
  audio?: VkAudio;
  doc?: VkDoc;
  link?: VkLink;
}

export interface VkPhoto {
  id: number;
  album_id: number;
  owner_id: number;
  user_id?: number;
  text: string;
  date: number;
  sizes: VkPhotoSize[];
}

export interface VkPhotoSize {
  type: 's' | 'm' | 'x' | 'o' | 'p' | 'q' | 'r' | 'y' | 'z' | 'w';
  url: string;
  width: number;
  height: number;
}

export interface VkVideo {
  id: number;
  owner_id: number;
  title: string;
  description: string;
  duration: number;
  date: number;
  views: number;
}

export interface VkAudio {
  id: number;
  owner_id: number;
  artist: string;
  title: string;
  duration: number;
  url?: string;
  date?: number;
}

export interface VkDoc {
  id: number;
  owner_id: number;
  title: string;
  size: number;
  ext: string;
  url: string;
  date: number;
  type: number;
}

export interface VkLink {
  url: string;
  title: string;
  caption?: string;
  description?: string;
  photo?: VkPhoto;
}

export interface VkApiResponse<T> {
  response: T;
}

export interface VkApiError {
  error_code: number;
  error_msg: string;
  request_params?: Array<{
    key: string;
    value: string;
  }>;
}

export interface VkWallGetResponse {
  count: number;
  items: VkPost[];
  profiles?: VkProfile[];
  groups?: VkGroup[];
}

export interface VkCommentsGetResponse {
  count: number;
  items: VkComment[];
  profiles?: VkProfile[];
  groups?: VkGroup[];
  current_level_count?: number;
  can_post?: 0 | 1;
}

export interface VkProfile {
  id: number;
  first_name: string;
  last_name: string;
  photo_50?: string;
  photo_100?: string;
  deactivated?: string;
  is_closed?: boolean;
}

export interface VkGroupsGetByIdResponse {
  items: VkGroup[];
}

export interface VkApiRequestOptions {
  method: string;
  params: Record<string, any>;
  retries?: number;
  timeout?: number;
}