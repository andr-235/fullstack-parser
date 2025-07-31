import { BaseEntity } from './vk-group.model';

export interface KeywordBase {
  word: string;
  category?: string;
  description?: string;
  is_active: boolean;
  is_case_sensitive: boolean;
  is_whole_word: boolean;
}

export interface KeywordCreate {
  word: string;
  category?: string;
  priority?: 'low' | 'medium' | 'high';
  is_active?: boolean;
}

export interface KeywordUpdate {
  word?: string;
  category?: string;
  priority?: 'low' | 'medium' | 'high';
  is_active?: boolean;
}

export interface KeywordResponse {
  id: number;
  word: string;
  category: string;
  is_active: boolean;
  priority: 'low' | 'medium' | 'high';
  created_at: string;
  updated_at: string;
  usage_count: number;
  last_used_at?: string;
}

export interface KeywordStats {
  total_keywords: number;
  active_keywords: number;
  inactive_keywords: number;
  high_priority_keywords: number;
  medium_priority_keywords: number;
  low_priority_keywords: number;
  total_usage_count: number;
  most_used_keywords: KeywordResponse[];
}
