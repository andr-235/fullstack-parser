import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatListModule } from '@angular/material/list';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialogModule } from '@angular/material/dialog';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { Subject, takeUntil, interval } from 'rxjs';

// Define interfaces locally since the service might not exist yet
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
  database_size: number;
  tables_count: number;
  total_records: number;
  active_connections: number;
  response_time: number;
  table_stats: Array<{
    name: string;
    records: number;
    size: number;
  }>;
}

export interface ActivityLog {
  id: number;
  timestamp: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  component: string;
  details?: string;
}

// Mock service for now - will be replaced with actual service
class MockMonitoringService {
  getSystemMetrics() {
    return new Subject<SystemMetrics>();
  }

  getParserMetrics() {
    return new Subject<ParserMetrics>();
  }

  getDatabaseMetrics() {
    return new Subject<DatabaseMetrics>();
  }

  getActivityLogs() {
    return new Subject<{ data: ActivityLog[]; total: number }>();
  }

  exportReport() {
    return new Subject<any>();
  }

  clearLogs() {
    return new Subject<void>();
  }
}

@Component({
  selector: 'app-monitoring',
  templateUrl: './monitoring.component.html',
  styleUrls: ['./monitoring.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatSelectModule,
    MatExpansionModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatListModule,
    MatDividerModule,
    MatTooltipModule,
    MatDialogModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatDatepickerModule,
    MatNativeDateModule,
  ],
})
export class MonitoringComponent implements OnInit, OnDestroy {
  systemMetrics?: SystemMetrics;
  parserMetrics?: ParserMetrics;
  databaseMetrics?: DatabaseMetrics;
  activityLogs: ActivityLog[] = [];
  filteredLogs: ActivityLog[] = [];

  isLoading = false;
  autoRefresh = false;
  selectedLogLevel = 'all';

  totalLogs = 0;
  currentPage = 0;
  pageSize = 25;

  private destroy$ = new Subject<void>();
  private refreshInterval?: any;

  constructor(
    private monitoringService: MockMonitoringService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadAllMetrics();
    this.loadActivityLogs();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }

  refreshData(): void {
    this.isLoading = true;
    this.loadAllMetrics();
    this.loadActivityLogs();
  }

  toggleAutoRefresh(): void {
    this.autoRefresh = !this.autoRefresh;

    if (this.autoRefresh) {
      this.refreshInterval = setInterval(() => {
        this.loadAllMetrics();
      }, 30000); // Refresh every 30 seconds
    } else {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
        this.refreshInterval = undefined;
      }
    }
  }

  exportReport(): void {
    this.monitoringService.exportReport().subscribe({
      next: (data: any) => {
        const blob = new Blob([JSON.stringify(data, null, 2)], {
          type: 'application/json',
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `monitoring-report-${
          new Date().toISOString().split('T')[0]
        }.json`;
        a.click();
        window.URL.revokeObjectURL(url);
        this.snackBar.open('Отчет экспортирован', 'Закрыть', {
          duration: 3000,
        });
      },
      error: (error: any) => {
        console.error('Error exporting report:', error);
        this.snackBar.open('Ошибка экспорта отчета', 'Закрыть', {
          duration: 3000,
        });
      },
    });
  }

  filterLogs(): void {
    if (this.selectedLogLevel === 'all') {
      this.filteredLogs = [...this.activityLogs];
    } else {
      this.filteredLogs = this.activityLogs.filter(
        (log) => log.level.toLowerCase() === this.selectedLogLevel
      );
    }
  }

  clearLogs(): void {
    this.monitoringService.clearLogs().subscribe({
      next: () => {
        this.activityLogs = [];
        this.filteredLogs = [];
        this.snackBar.open('Журнал очищен', 'Закрыть', { duration: 3000 });
      },
      error: (error: any) => {
        console.error('Error clearing logs:', error);
        this.snackBar.open('Ошибка очистки журнала', 'Закрыть', {
          duration: 3000,
        });
      },
    });
  }

  private loadAllMetrics(): void {
    this.monitoringService.getSystemMetrics().subscribe({
      next: (metrics: SystemMetrics) => {
        this.systemMetrics = metrics;
        this.isLoading = false;
      },
      error: (error: any) => {
        console.error('Error loading system metrics:', error);
        this.snackBar.open('Ошибка загрузки метрик системы', 'Закрыть', {
          duration: 3000,
        });
        this.isLoading = false;
      },
    });

    this.monitoringService.getParserMetrics().subscribe({
      next: (metrics: ParserMetrics) => {
        this.parserMetrics = metrics;
      },
      error: (error: any) => {
        console.error('Error loading parser metrics:', error);
        this.snackBar.open('Ошибка загрузки метрик парсера', 'Закрыть', {
          duration: 3000,
        });
      },
    });

    this.monitoringService.getDatabaseMetrics().subscribe({
      next: (metrics: DatabaseMetrics) => {
        this.databaseMetrics = metrics;
      },
      error: (error: any) => {
        console.error('Error loading database metrics:', error);
        this.snackBar.open('Ошибка загрузки метрик БД', 'Закрыть', {
          duration: 3000,
        });
      },
    });
  }

  private loadActivityLogs(): void {
    this.monitoringService.getActivityLogs().subscribe({
      next: (response: { data: ActivityLog[]; total: number }) => {
        this.activityLogs = response.data;
        this.totalLogs = response.total;
        this.filterLogs();
      },
      error: (error: any) => {
        console.error('Error loading activity logs:', error);
        this.snackBar.open('Ошибка загрузки журнала активности', 'Закрыть', {
          duration: 3000,
        });
      },
    });
  }

  formatUptime(seconds: number): string {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (days > 0) {
      return `${days}д ${hours}ч ${minutes}м`;
    } else if (hours > 0) {
      return `${hours}ч ${minutes}м`;
    } else {
      return `${minutes}м`;
    }
  }

  formatDateTime(dateString: string): string {
    return new Date(dateString).toLocaleString('ru-RU');
  }

  formatBytes(bytes: number): string {
    if (bytes === 0) return '0 Б';
    const k = 1024;
    const sizes = ['Б', 'КБ', 'МБ', 'ГБ'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}
