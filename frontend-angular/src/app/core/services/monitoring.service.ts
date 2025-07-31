import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_activity: number;
  active_connections: number;
  uptime: number;
}

export interface ParserMetrics {
  is_running: boolean;
  total_groups: number;
  active_groups: number;
  total_comments_parsed: number;
  comments_with_keywords: number;
  errors_count: number;
  last_parse_time?: string;
  current_progress?: {
    group_name: string;
    progress_percentage: number;
    comments_processed: number;
  };
}

export interface DatabaseMetrics {
  total_groups: number;
  total_keywords: number;
  total_comments: number;
  new_comments_today: number;
  new_comments_this_week: number;
  database_size: number;
  last_backup?: string;
}

export interface ActivityLog {
  id: number;
  timestamp: string;
  level: 'INFO' | 'WARNING' | 'ERROR';
  message: string;
  component: string;
  details?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

@Injectable({
  providedIn: 'root',
})
export class MonitoringService {
  private baseUrl = `${environment.apiUrl}/monitoring`;

  constructor(private http: HttpClient) {}

  /**
   * Get system metrics (CPU, memory, disk, network)
   */
  getSystemMetrics(): Observable<SystemMetrics> {
    return this.http.get<SystemMetrics>(`${this.baseUrl}/system-metrics`);
  }

  /**
   * Get parser metrics and status
   */
  getParserMetrics(): Observable<ParserMetrics> {
    return this.http.get<ParserMetrics>(`${this.baseUrl}/parser-metrics`);
  }

  /**
   * Get database metrics and statistics
   */
  getDatabaseMetrics(): Observable<DatabaseMetrics> {
    return this.http.get<DatabaseMetrics>(`${this.baseUrl}/database-metrics`);
  }

  /**
   * Get activity logs with pagination and filtering
   */
  getActivityLogs(
    page: number = 0,
    size: number = 25,
    level?: string,
    component?: string,
    startDate?: string,
    endDate?: string
  ): Observable<PaginatedResponse<ActivityLog>> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('size', size.toString());

    if (level) {
      params = params.set('level', level);
    }

    if (component) {
      params = params.set('component', component);
    }

    if (startDate) {
      params = params.set('start_date', startDate);
    }

    if (endDate) {
      params = params.set('end_date', endDate);
    }

    return this.http.get<PaginatedResponse<ActivityLog>>(
      `${this.baseUrl}/activity-logs`,
      { params }
    );
  }

  /**
   * Get detailed activity log by ID
   */
  getActivityLogById(id: number): Observable<ActivityLog> {
    return this.http.get<ActivityLog>(`${this.baseUrl}/activity-logs/${id}`);
  }

  /**
   * Clear activity logs
   */
  clearActivityLogs(): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/activity-logs`);
  }

  /**
   * Get system health status
   */
  getSystemHealth(): Observable<{
    status: 'healthy' | 'warning' | 'critical';
    checks: {
      database: boolean;
      parser: boolean;
      api: boolean;
      disk: boolean;
      memory: boolean;
    };
    message?: string;
  }> {
    return this.http.get<{
      status: 'healthy' | 'warning' | 'critical';
      checks: {
        database: boolean;
        parser: boolean;
        api: boolean;
        disk: boolean;
        memory: boolean;
      };
      message?: string;
    }>(`${this.baseUrl}/health`);
  }

  /**
   * Get performance metrics
   */
  getPerformanceMetrics(): Observable<{
    response_time: number;
    requests_per_second: number;
    error_rate: number;
    active_users: number;
  }> {
    return this.http.get<{
      response_time: number;
      requests_per_second: number;
      error_rate: number;
      active_users: number;
    }>(`${this.baseUrl}/performance`);
  }

  /**
   * Get backup status and history
   */
  getBackupStatus(): Observable<{
    last_backup: string;
    backup_size: number;
    backup_status: 'success' | 'failed' | 'in_progress';
    next_scheduled_backup: string;
    backup_retention_days: number;
  }> {
    return this.http.get<{
      last_backup: string;
      backup_size: number;
      backup_status: 'success' | 'failed' | 'in_progress';
      next_scheduled_backup: string;
      backup_retention_days: number;
    }>(`${this.baseUrl}/backup-status`);
  }

  /**
   * Trigger manual backup
   */
  triggerBackup(): Observable<{ message: string; backup_id: string }> {
    return this.http.post<{ message: string; backup_id: string }>(
      `${this.baseUrl}/backup`,
      {}
    );
  }

  /**
   * Get system alerts
   */
  getSystemAlerts(): Observable<
    {
      id: number;
      timestamp: string;
      level: 'info' | 'warning' | 'critical';
      message: string;
      component: string;
      acknowledged: boolean;
    }[]
  > {
    return this.http.get<
      {
        id: number;
        timestamp: string;
        level: 'info' | 'warning' | 'critical';
        message: string;
        component: string;
        acknowledged: boolean;
      }[]
    >(`${this.baseUrl}/alerts`);
  }

  /**
   * Acknowledge system alert
   */
  acknowledgeAlert(alertId: number): Observable<void> {
    return this.http.patch<void>(
      `${this.baseUrl}/alerts/${alertId}/acknowledge`,
      {}
    );
  }

  /**
   * Get system configuration
   */
  getSystemConfig(): Observable<{
    auto_backup_enabled: boolean;
    backup_schedule: string;
    log_retention_days: number;
    alert_thresholds: {
      cpu_warning: number;
      cpu_critical: number;
      memory_warning: number;
      memory_critical: number;
      disk_warning: number;
      disk_critical: number;
    };
  }> {
    return this.http.get<{
      auto_backup_enabled: boolean;
      backup_schedule: string;
      log_retention_days: number;
      alert_thresholds: {
        cpu_warning: number;
        cpu_critical: number;
        memory_warning: number;
        memory_critical: number;
        disk_warning: number;
        disk_critical: number;
      };
    }>(`${this.baseUrl}/config`);
  }

  /**
   * Update system configuration
   */
  updateSystemConfig(config: {
    auto_backup_enabled?: boolean;
    backup_schedule?: string;
    log_retention_days?: number;
    alert_thresholds?: {
      cpu_warning?: number;
      cpu_critical?: number;
      memory_warning?: number;
      memory_critical?: number;
      disk_warning?: number;
      disk_critical?: number;
    };
  }): Observable<{ message: string }> {
    return this.http.put<{ message: string }>(`${this.baseUrl}/config`, config);
  }
}
