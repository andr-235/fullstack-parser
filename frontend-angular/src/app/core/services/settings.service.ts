import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface GeneralSettings {
  application_name: string;
  default_language: string;
  timezone: string;
  date_format: string;
  time_format: string;
  auto_save_interval: number;
}

export interface ParserSettings {
  max_concurrent_groups: number;
  parse_interval_minutes: number;
  max_comments_per_group: number;
  enable_auto_parsing: boolean;
  enable_keyword_filtering: boolean;
  enable_sentiment_analysis: boolean;
  save_raw_data: boolean;
  retry_failed_requests: boolean;
  max_retry_attempts: number;
}

export interface NotificationSettings {
  enable_email_notifications: boolean;
  enable_browser_notifications: boolean;
  notify_on_parse_completion: boolean;
  notify_on_errors: boolean;
  notify_on_new_keywords: boolean;
  notification_sound: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start: string;
  quiet_hours_end: string;
}

export interface SecuritySettings {
  session_timeout_minutes: number;
  require_password_change: boolean;
  password_change_interval_days: number;
  enable_two_factor: boolean;
  max_login_attempts: number;
  lockout_duration_minutes: number;
  enable_audit_log: boolean;
  log_retention_days: number;
}

export interface AppearanceSettings {
  theme: string;
  primary_color: string;
  accent_color: string;
  font_size: string;
  compact_mode: boolean;
  show_animations: boolean;
  sidebar_collapsed: boolean;
  dashboard_layout: string;
}

export interface ApplicationSettings {
  general: GeneralSettings;
  parser: ParserSettings;
  notifications: NotificationSettings;
  security: SecuritySettings;
  appearance: AppearanceSettings;
}

@Injectable({
  providedIn: 'root',
})
export class SettingsService {
  private readonly apiUrl = `${environment.apiUrl}/settings`;

  constructor(private http: HttpClient) {}

  getSettings(): Observable<ApplicationSettings> {
    return this.http.get<ApplicationSettings>(this.apiUrl);
  }

  updateSettings(
    settings: ApplicationSettings
  ): Observable<ApplicationSettings> {
    return this.http.put<ApplicationSettings>(this.apiUrl, settings);
  }

  resetToDefaults(): Observable<ApplicationSettings> {
    return this.http.post<ApplicationSettings>(`${this.apiUrl}/reset`, {});
  }

  exportSettings(): Observable<ApplicationSettings> {
    return this.http.get<ApplicationSettings>(`${this.apiUrl}/export`);
  }

  importSettings(
    settings: ApplicationSettings
  ): Observable<ApplicationSettings> {
    return this.http.post<ApplicationSettings>(
      `${this.apiUrl}/import`,
      settings
    );
  }

  getDefaultSettings(): ApplicationSettings {
    return {
      general: {
        application_name: 'VK Parser',
        default_language: 'ru',
        timezone: 'Europe/Moscow',
        date_format: 'DD.MM.YYYY',
        time_format: '24',
        auto_save_interval: 5,
      },
      parser: {
        max_concurrent_groups: 3,
        parse_interval_minutes: 15,
        max_comments_per_group: 1000,
        enable_auto_parsing: true,
        enable_keyword_filtering: true,
        enable_sentiment_analysis: false,
        save_raw_data: true,
        retry_failed_requests: true,
        max_retry_attempts: 3,
      },
      notifications: {
        enable_email_notifications: true,
        enable_browser_notifications: true,
        notify_on_parse_completion: true,
        notify_on_errors: true,
        notify_on_new_keywords: false,
        notification_sound: true,
        quiet_hours_enabled: false,
        quiet_hours_start: '22:00',
        quiet_hours_end: '08:00',
      },
      security: {
        session_timeout_minutes: 30,
        require_password_change: false,
        password_change_interval_days: 90,
        enable_two_factor: false,
        max_login_attempts: 5,
        lockout_duration_minutes: 15,
        enable_audit_log: true,
        log_retention_days: 90,
      },
      appearance: {
        theme: 'light',
        primary_color: '#1976d2',
        accent_color: '#ff4081',
        font_size: 'medium',
        compact_mode: false,
        show_animations: true,
        sidebar_collapsed: false,
        dashboard_layout: 'grid',
      },
    };
  }

  validateSettings(settings: ApplicationSettings): boolean {
    // Validate general settings
    if (
      !settings.general?.application_name ||
      settings.general.application_name.trim() === ''
    ) {
      return false;
    }

    // Validate parser settings
    if (
      settings.parser?.max_concurrent_groups < 1 ||
      settings.parser?.max_concurrent_groups > 10
    ) {
      return false;
    }

    if (
      settings.parser?.parse_interval_minutes < 5 ||
      settings.parser?.parse_interval_minutes > 1440
    ) {
      return false;
    }

    // Validate security settings
    if (
      settings.security?.session_timeout_minutes < 5 ||
      settings.security?.session_timeout_minutes > 480
    ) {
      return false;
    }

    return true;
  }

  applyThemeSettings(appearance: AppearanceSettings): void {
    // Apply theme to document
    document.documentElement.setAttribute('data-theme', appearance.theme);

    // Apply custom colors if needed
    if (appearance.primary_color) {
      document.documentElement.style.setProperty(
        '--primary-color',
        appearance.primary_color
      );
    }

    if (appearance.accent_color) {
      document.documentElement.style.setProperty(
        '--accent-color',
        appearance.accent_color
      );
    }

    // Apply font size
    document.documentElement.setAttribute(
      'data-font-size',
      appearance.font_size
    );
  }
}
