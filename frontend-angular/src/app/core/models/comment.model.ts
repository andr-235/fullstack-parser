import { BaseEntity } from './vk-group.model';
import { VKGroupResponse } from './vk-group.model';
import { KeywordResponse } from './keyword.model';

export interface VKCommentBase {
  text: string;
  author_id: number;
  author_name?: string;
  published_at: string;
}

export interface VKCommentResponse extends VKCommentBase, BaseEntity {
  vk_id: number;
  post_id: number;
  post_vk_id?: number;
  author_screen_name?: string;
  author_photo_url?: string;
  likes_count: number;
  parent_comment_id?: number;
  has_attachments: boolean;
  matched_keywords_count: number;
  is_processed: boolean;
  processed_at?: string;
  is_viewed: boolean;
  viewed_at?: string;
  is_archived: boolean;
  archived_at?: string;
  group?: VKGroupResponse;
  matched_keywords?: string[];
}

export interface CommentWithKeywords extends VKCommentResponse {
  matched_keywords: string[];
  keyword_matches: Array<{
    keyword: string;
    matched_text: string;
    position: number;
    context: string;
  }>;
}

export interface CommentUpdateRequest {
  is_viewed?: boolean;
  is_archived?: boolean;
}

export interface CommentSearchParams {
  text?: string;
  group_id?: number;
  keyword_id?: number;
  author_id?: number;
  author_screen_name?: string[];
  date_from?: string;
  date_to?: string;
  is_viewed?: boolean;
  is_archived?: boolean;
  order_by?: string;
  order_dir?: string;
}
