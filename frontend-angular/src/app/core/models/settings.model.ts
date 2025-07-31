export interface ApplicationSettings {
  general: GeneralSettings;
  parser: ParserSettings;
  notifications: NotificationSettings;
  security: SecuritySettings;
  appearance: AppearanceSettings;
}

export interface GeneralSettings {
  language: string;
  timezone: string;
  date_format: string;
  time_format: string;
  currency: string;
  auto_save: boolean;
  auto_save_interval: number;
}

export interface ParserSettings {
  enabled: boolean;
  interval_minutes: number;
  max_posts_per_group: number;
  max_comments_per_post: number;
  keywords_case_sensitive: boolean;
  keywords_whole_word: boolean;
  sentiment_analysis_enabled: boolean;
  auto_archive_old_comments: boolean;
  archive_days_threshold: number;
}

export interface NotificationSettings {
  email_notifications: boolean;
  browser_notifications: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start: string;
  quiet_hours_end: string;
  notification_types: {
    new_comments: boolean;
    parsing_errors: boolean;
    system_alerts: boolean;
    keyword_matches: boolean;
  };
}

export interface SecuritySettings {
  session_timeout_minutes: number;
  max_login_attempts: number;
  require_password_change_days: number;
  two_factor_enabled: boolean;
  audit_log_enabled: boolean;
  ip_whitelist: string[];
}

export interface AppearanceSettings {
  theme: 'light' | 'dark' | 'auto';
  primary_color: string;
  accent_color: string;
  sidebar_collapsed: boolean;
  compact_mode: boolean;
  animations_enabled: boolean;
  font_size: 'small' | 'medium' | 'large';
}
