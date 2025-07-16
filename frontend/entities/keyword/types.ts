import { BaseEntity } from "@/shared/types/api";

// Keyword типы
export interface KeywordBase {
  word: string;
  category?: string;
  description?: string;
  is_active: boolean;
  is_case_sensitive: boolean;
  is_whole_word: boolean;
}

export interface KeywordCreate extends KeywordBase {}

export interface KeywordUpdate {
  word?: string;
  category?: string;
  description?: string;
  is_active?: boolean;
  is_case_sensitive?: boolean;
  is_whole_word?: boolean;
}

export interface KeywordResponse extends KeywordBase, BaseEntity {
  total_matches: number;
}

export interface KeywordStats {
  keyword_id: number;
  word: string;
  total_matches: number;
  recent_matches: number;
  top_groups: string[];
}
