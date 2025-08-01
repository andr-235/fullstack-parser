import {
  Component,
  OnInit,
  OnDestroy,
  ChangeDetectionStrategy,
  inject,
  signal,
  computed,
} from '@angular/core';
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
  changeDetection: ChangeDetectionStrategy.OnPush,
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
  // Используем signals для лучшей производительности
  systemMetrics = signal<SystemMetrics | undefined>(undefined);
  parserMetrics = signal<ParserMetrics | undefined>(undefined);
  databaseMetrics = signal<DatabaseMetrics | undefined>(undefined);
  activityLogs = signal<ActivityLog[]>([]);
  filteredLogs = signal<ActivityLog[]>([]);
  isLoading = signal(false);
  autoRefresh = signal(false);
  selectedLogLevel = signal('all');
  totalLogs = signal(0);
  currentPage = signal(0);
  pageSize = signal(25);

  // Computed values
  hasLogs = computed(() => this.activityLogs().length > 0);
  hasFilteredLogs = computed(() => this.filteredLogs().length > 0);
  isParserRunning = computed(() => this.parserMetrics()?.is_running || false);

  // Геттеры для template
  get systemMetricsData(): SystemMetrics | undefined {
    return this.systemMetrics();
  }

  get parserMetricsData(): ParserMetrics | undefined {
    return this.parserMetrics();
  }

  get databaseMetricsData(): DatabaseMetrics | undefined {
    return this.databaseMetrics();
  }

  get activityLogsData(): ActivityLog[] {
    return this.activityLogs();
  }

  get filteredLogsData(): ActivityLog[] {
    return this.filteredLogs();
  }

  get isLoadingData(): boolean {
    return this.isLoading();
  }

  get autoRefreshData(): boolean {
    return this.autoRefresh();
  }

  get selectedLogLevelData(): string {
    return this.selectedLogLevel();
  }

  get totalLogsCount(): number {
    return this.totalLogs();
  }

  get currentPageIndex(): number {
    return this.currentPage();
  }

  get pageSizeValue(): number {
    return this.pageSize();
  }

  displayedColumns = ['timestamp', 'level', 'component', 'message', 'actions'];

  private destroy$ = new Subject<void>();
  private refreshInterval?: any;

  // Используем inject() вместо constructor injection
  private monitoringService = inject(MockMonitoringService);
  private snackBar = inject(MatSnackBar);

  constructor() {}

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
    this.loadAllMetrics();
    this.loadActivityLogs();
  }

  toggleAutoRefresh(): void {
    const current = this.autoRefresh();
    this.autoRefresh.set(!current);

    if (!current) {
      this.refreshInterval = setInterval(() => {
        this.refreshData();
      }, 30000); // Refresh every 30 seconds
    } else {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
        this.refreshInterval = undefined;
      }
    }
  }

  exportReport(): void {
    this.isLoading.set(true);
    this.monitoringService.exportReport().subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `monitoring_report_${
          new Date().toISOString().split('T')[0]
        }.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        this.snackBar.open('Report exported successfully', 'Close', {
          duration: 2000,
        });
        this.isLoading.set(false);
      },
      error: (error) => {
        console.error('Error exporting report:', error);
        this.snackBar.open('Error exporting report', 'Close', {
          duration: 3000,
        });
        this.isLoading.set(false);
      },
    });
  }

  filterLogs(): void {
    const level = this.selectedLogLevel();
    const logs = this.activityLogs();

    if (level === 'all') {
      this.filteredLogs.set(logs);
    } else {
      const filtered = logs.filter((log) => log.level === level);
      this.filteredLogs.set(filtered);
    }
  }

  clearLogs(): void {
    this.monitoringService.clearLogs().subscribe({
      next: () => {
        this.snackBar.open('Logs cleared successfully', 'Close', {
          duration: 2000,
        });
        this.loadActivityLogs();
      },
      error: (error) => {
        console.error('Error clearing logs:', error);
        this.snackBar.open('Error clearing logs', 'Close', {
          duration: 3000,
        });
      },
    });
  }

  private loadAllMetrics(): void {
    this.isLoading.set(true);

    // Load system metrics
    this.monitoringService.getSystemMetrics().subscribe({
      next: (metrics) => {
        this.systemMetrics.set(metrics);
      },
      error: (error) => {
        console.error('Error loading system metrics:', error);
      },
    });

    // Load parser metrics
    this.monitoringService.getParserMetrics().subscribe({
      next: (metrics) => {
        this.parserMetrics.set(metrics);
      },
      error: (error) => {
        console.error('Error loading parser metrics:', error);
      },
    });

    // Load database metrics
    this.monitoringService.getDatabaseMetrics().subscribe({
      next: (metrics) => {
        this.databaseMetrics.set(metrics);
        this.isLoading.set(false);
      },
      error: (error) => {
        console.error('Error loading database metrics:', error);
        this.isLoading.set(false);
      },
    });
  }

  private loadActivityLogs(): void {
    this.monitoringService.getActivityLogs().subscribe({
      next: (response) => {
        this.activityLogs.set(response.data);
        this.totalLogs.set(response.total);
        this.filterLogs();
      },
      error: (error) => {
        console.error('Error loading activity logs:', error);
      },
    });
  }

  formatUptime(seconds: number): string {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`;
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  }

  formatDateTime(dateString: string): string {
    return new Date(dateString).toLocaleString();
  }

  formatBytes(bytes: number): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i];
  }
}
