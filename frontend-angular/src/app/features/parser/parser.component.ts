import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormControl, FormGroup } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatListModule } from '@angular/material/list';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialogModule } from '@angular/material/dialog';
import { Subject, takeUntil, interval } from 'rxjs';

import {
  ParserService,
  ParserStatus,
  ParserConfig,
  ParserLog,
} from '../../core/services/parser.service';
import { GroupsService } from '../../core/services/groups.service';
import { VKGroupResponse } from '../../core/models';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-parser',
  template: `
    <div class="parser-container">
      <!-- Status Card -->
      <mat-card class="status-card">
        <mat-card-header>
          <mat-card-title>Parser Status</mat-card-title>
          <mat-card-subtitle
            >Monitor and control VK parsing operations</mat-card-subtitle
          >
        </mat-card-header>
        <mat-card-content>
          <div *ngIf="loading" class="loading-section">
            <app-loading-spinner
              message="Loading parser status..."
            ></app-loading-spinner>
          </div>

          <div *ngIf="!loading && status" class="status-content">
            <!-- Status Overview -->
            <div class="status-overview">
              <div class="status-indicator">
                <mat-icon [class]="status.is_running ? 'running' : 'stopped'">
                  {{ status.is_running ? 'play_circle' : 'stop_circle' }}
                </mat-icon>
                <span class="status-text">{{
                  status.is_running ? 'Running' : 'Stopped'
                }}</span>
              </div>

              <div class="status-stats">
                <div class="stat-item">
                  <div class="stat-value">{{ status.total_groups }}</div>
                  <div class="stat-label">Total Groups</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ status.active_groups }}</div>
                  <div class="stat-label">Active Groups</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">
                    {{ status.total_comments_parsed | number }}
                  </div>
                  <div class="stat-label">Comments Parsed</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">
                    {{ status.comments_with_keywords | number }}
                  </div>
                  <div class="stat-label">With Keywords</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ status.errors_count }}</div>
                  <div class="stat-label">Errors</div>
                </div>
              </div>
            </div>

            <!-- Current Progress -->
            <div *ngIf="status.current_progress" class="progress-section">
              <h3>Current Progress</h3>
              <div class="progress-info">
                <div class="progress-group">
                  {{ status.current_progress.group_name }}
                </div>
                <div class="progress-bar">
                  <mat-progress-bar
                    [value]="status.current_progress.progress_percentage"
                    color="primary"
                  ></mat-progress-bar>
                  <span class="progress-text"
                    >{{ status.current_progress.progress_percentage }}%</span
                  >
                </div>
                <div class="progress-details">
                  Comments parsed: {{ status.current_progress.comments_parsed }}
                </div>
              </div>
            </div>

            <!-- Timing Info -->
            <div class="timing-info">
              <div *ngIf="status.last_run" class="timing-item">
                <mat-icon>schedule</mat-icon>
                <span>Last run: {{ status.last_run | date : 'medium' }}</span>
              </div>
              <div *ngIf="status.next_run" class="timing-item">
                <mat-icon>update</mat-icon>
                <span>Next run: {{ status.next_run | date : 'medium' }}</span>
              </div>
            </div>
          </div>
        </mat-card-content>
      </mat-card>

      <!-- Control Card -->
      <mat-card class="control-card">
        <mat-card-header>
          <mat-card-title>Parser Controls</mat-card-title>
          <mat-card-subtitle
            >Start, stop, and configure parsing operations</mat-card-subtitle
          >
        </mat-card-header>
        <mat-card-content>
          <div class="control-buttons">
            <button
              mat-raised-button
              color="primary"
              [disabled]="status?.is_running"
              (click)="startParsing()"
            >
              <mat-icon>play_arrow</mat-icon>
              Start Parsing
            </button>
            <button
              mat-raised-button
              color="warn"
              [disabled]="!status?.is_running"
              (click)="stopParsing()"
            >
              <mat-icon>stop</mat-icon>
              Stop Parsing
            </button>
            <button mat-raised-button color="accent" (click)="parseAllGroups()">
              <mat-icon>refresh</mat-icon>
              Parse All Groups
            </button>
          </div>

          <!-- Group Selection -->
          <div class="group-selection">
            <h3>Parse Specific Groups</h3>
            <div class="group-list">
              <mat-checkbox
                *ngFor="let group of groups"
                [checked]="selectedGroups.includes(group.id)"
                (change)="toggleGroupSelection(group.id)"
              >
                {{ group.name }}
              </mat-checkbox>
            </div>
            <button
              mat-raised-button
              color="accent"
              [disabled]="selectedGroups.length === 0"
              (click)="parseSelectedGroups()"
            >
              Parse Selected Groups
            </button>
          </div>
        </mat-card-content>
      </mat-card>

      <!-- Configuration Card -->
      <mat-card class="config-card">
        <mat-card-header>
          <mat-card-title>Parser Configuration</mat-card-title>
          <mat-card-subtitle
            >Configure parsing behavior and settings</mat-card-subtitle
          >
        </mat-card-header>
        <mat-card-content>
          <div *ngIf="config" class="config-form">
            <div class="config-options">
              <mat-form-field appearance="outline">
                <mat-label>Parse Interval (minutes)</mat-label>
                <input
                  matInput
                  type="number"
                  [formControl]="parseIntervalMinutesControl"
                  min="5"
                  max="1440"
                />
                <mat-error *ngIf="parseIntervalMinutesControl.hasError('min')">
                  Минимум 5 минут
                </mat-error>
                <mat-error *ngIf="parseIntervalMinutesControl.hasError('max')">
                  Максимум 1440 минут
                </mat-error>
              </mat-form-field>

              <mat-form-field appearance="outline">
                <mat-label>Максимум постов на группу</mat-label>
                <input
                  matInput
                  type="number"
                  [formControl]="maxPostsPerGroupControl"
                  min="10"
                  max="1000"
                />
                <mat-error *ngIf="maxPostsPerGroupControl.hasError('min')">
                  Минимум 10 постов
                </mat-error>
                <mat-error *ngIf="maxPostsPerGroupControl.hasError('max')">
                  Максимум 1000 постов
                </mat-error>
              </mat-form-field>

              <mat-form-field appearance="outline">
                <mat-label>Максимум комментариев на пост</mat-label>
                <input
                  matInput
                  type="number"
                  [formControl]="maxCommentsPerPostControl"
                  min="10"
                  max="5000"
                />
                <mat-error *ngIf="maxCommentsPerPostControl.hasError('min')">
                  Минимум 10 комментариев
                </mat-error>
                <mat-error *ngIf="maxCommentsPerPostControl.hasError('max')">
                  Максимум 5000 комментариев
                </mat-error>
              </mat-form-field>

              <mat-form-field appearance="outline">
                <mat-label>Задержка между запросами (сек)</mat-label>
                <input
                  matInput
                  type="number"
                  [formControl]="parseDelaySecondsControl"
                  min="1"
                  max="10"
                />
                <mat-error *ngIf="parseDelaySecondsControl.hasError('min')">
                  Минимум 1 секунда
                </mat-error>
                <mat-error *ngIf="parseDelaySecondsControl.hasError('max')">
                  Максимум 10 секунд
                </mat-error>
              </mat-form-field>
            </div>

            <div class="config-options">
              <mat-checkbox [formControl]="autoParseEnabledControl">
                Автоматический парсинг
              </mat-checkbox>
            </div>

            <div class="config-actions">
              <button mat-raised-button color="primary" (click)="saveConfig()">
                Save Configuration
              </button>
            </div>
          </div>
        </mat-card-content>
      </mat-card>

      <!-- Logs Card -->
      <mat-card class="logs-card">
        <mat-card-header>
          <mat-card-title>Parser Logs</mat-card-title>
          <mat-card-subtitle
            >Recent parsing activity and errors</mat-card-subtitle
          >
        </mat-card-header>
        <mat-card-content>
          <div class="logs-actions">
            <button mat-raised-button color="warn" (click)="clearLogs()">
              <mat-icon>clear</mat-icon>
              Clear Logs
            </button>
          </div>

          <div class="logs-list">
            <div
              *ngFor="let log of logs"
              class="log-item"
              [class]="'log-' + log.level.toLowerCase()"
            >
              <div class="log-header">
                <span class="log-timestamp">{{
                  log.timestamp | date : 'short'
                }}</span>
                <mat-chip [color]="getLogLevelColor(log.level)" size="small">
                  {{ log.level }}
                </mat-chip>
                <span *ngIf="log.group_name" class="log-group">{{
                  log.group_name
                }}</span>
              </div>
              <div class="log-message">{{ log.message }}</div>
            </div>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [
    `
      .parser-container {
        padding: 20px;
        max-width: 1400px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
      }

      .status-card {
        grid-column: 1 / -1;
      }

      .control-card {
        grid-column: 1 / 2;
      }

      .config-card {
        grid-column: 2 / 3;
      }

      .logs-card {
        grid-column: 1 / -1;
      }

      .loading-section {
        display: flex;
        justify-content: center;
        padding: 40px;
      }

      .status-content {
        display: flex;
        flex-direction: column;
        gap: 20px;
      }

      .status-overview {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        background: #f5f5f5;
        border-radius: 8px;
      }

      .status-indicator {
        display: flex;
        align-items: center;
        gap: 10px;
      }

      .status-indicator mat-icon {
        font-size: 32px;
        width: 32px;
        height: 32px;
      }

      .status-indicator mat-icon.running {
        color: #4caf50;
      }

      .status-indicator mat-icon.stopped {
        color: #f44336;
      }

      .status-text {
        font-size: 18px;
        font-weight: 500;
      }

      .status-stats {
        display: flex;
        gap: 30px;
      }

      .stat-item {
        text-align: center;
      }

      .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #1976d2;
      }

      .stat-label {
        font-size: 12px;
        color: #666;
        text-transform: uppercase;
      }

      .progress-section {
        padding: 20px;
        background: #e3f2fd;
        border-radius: 8px;
      }

      .progress-section h3 {
        margin: 0 0 15px 0;
        color: #1976d2;
      }

      .progress-info {
        display: flex;
        flex-direction: column;
        gap: 10px;
      }

      .progress-group {
        font-weight: 500;
        color: #1976d2;
      }

      .progress-bar {
        display: flex;
        align-items: center;
        gap: 10px;
      }

      .progress-bar mat-progress-bar {
        flex: 1;
      }

      .progress-text {
        font-weight: 500;
        min-width: 50px;
      }

      .progress-details {
        font-size: 14px;
        color: #666;
      }

      .timing-info {
        display: flex;
        gap: 30px;
        padding: 15px;
        background: #f9f9f9;
        border-radius: 8px;
      }

      .timing-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        color: #666;
      }

      .control-buttons {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        flex-wrap: wrap;
      }

      .group-selection {
        margin-top: 20px;
      }

      .group-selection h3 {
        margin: 0 0 15px 0;
        color: #1976d2;
      }

      .group-list {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 10px;
        margin-bottom: 15px;
        max-height: 200px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
      }

      .config-form {
        display: flex;
        flex-direction: column;
        gap: 15px;
      }

      .config-options {
        display: flex;
        flex-direction: column;
        gap: 15px;
      }

      .config-actions {
        margin-top: 20px;
      }

      .logs-actions {
        margin-bottom: 20px;
      }

      .logs-list {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
      }

      .log-item {
        padding: 10px;
        border-bottom: 1px solid #e0e0e0;
      }

      .log-item:last-child {
        border-bottom: none;
      }

      .log-item.log-error {
        background-color: #ffebee;
      }

      .log-item.log-warning {
        background-color: #fff3e0;
      }

      .log-item.log-info {
        background-color: #e3f2fd;
      }

      .log-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 5px;
      }

      .log-timestamp {
        font-size: 12px;
        color: #666;
      }

      .log-group {
        font-size: 12px;
        color: #1976d2;
        font-weight: 500;
      }

      .log-message {
        font-size: 14px;
        line-height: 1.4;
      }

      @media (max-width: 768px) {
        .parser-container {
          grid-template-columns: 1fr;
        }

        .status-stats {
          flex-direction: column;
          gap: 15px;
        }

        .timing-info {
          flex-direction: column;
          gap: 10px;
        }
      }
    `,
  ],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatCheckboxModule,
    MatIconModule,
    MatSelectModule,
    MatExpansionModule,
    MatProgressBarModule,
    MatChipsModule,
    MatListModule,
    MatDividerModule,
    MatTooltipModule,
    MatDialogModule,
    LoadingSpinnerComponent,
  ],
})
export class ParserComponent implements OnInit, OnDestroy {
  status?: ParserStatus;
  config?: ParserConfig;
  groups: VKGroupResponse[] = [];
  logs: ParserLog[] = [];
  loading = false;
  selectedGroups: number[] = [];

  configForm = new FormGroup({
    auto_parse_enabled: new FormControl(false),
    parse_interval_minutes: new FormControl(30),
    max_posts_per_group: new FormControl(100),
    max_comments_per_post: new FormControl(100),
    parse_delay_seconds: new FormControl(1),
  });

  // Getters for config form controls
  get autoParseEnabledControl() {
    return this.configForm.get('auto_parse_enabled') as FormControl;
  }
  get parseIntervalMinutesControl() {
    return this.configForm.get('parse_interval_minutes') as FormControl;
  }
  get maxPostsPerGroupControl() {
    return this.configForm.get('max_posts_per_group') as FormControl;
  }
  get maxCommentsPerPostControl() {
    return this.configForm.get('max_comments_per_post') as FormControl;
  }
  get parseDelaySecondsControl() {
    return this.configForm.get('parse_delay_seconds') as FormControl;
  }

  private destroy$ = new Subject<void>();

  constructor(
    private parserService: ParserService,
    private groupsService: GroupsService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadStatus();
    this.loadConfig();
    this.loadGroups();
    this.loadLogs();

    // Auto-refresh status every 5 seconds
    interval(5000)
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.loadStatus();
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadStatus(): void {
    this.parserService.getParserStatus().subscribe({
      next: (status) => {
        this.status = status;
      },
      error: (error) => {
        console.error('Error loading parser status:', error);
      },
    });
  }

  private loadConfig(): void {
    this.parserService.getParserConfig().subscribe({
      next: (config) => {
        this.config = config;
        this.configForm.patchValue(config);
      },
      error: (error) => {
        console.error('Error loading parser config:', error);
      },
    });
  }

  private loadGroups(): void {
    this.groupsService.getGroups({ size: 100 }).subscribe({
      next: (response) => {
        this.groups = response.items;
      },
      error: (error) => {
        console.error('Error loading groups:', error);
      },
    });
  }

  private loadLogs(): void {
    this.parserService.getParserLogs(50).subscribe({
      next: (logs) => {
        this.logs = logs;
      },
      error: (error) => {
        console.error('Error loading parser logs:', error);
      },
    });
  }

  startParsing(): void {
    this.parserService.startParsing().subscribe({
      next: (response) => {
        this.snackBar.open(response.message, 'Close', { duration: 2000 });
        this.loadStatus();
      },
      error: (error) => {
        console.error('Error starting parser:', error);
        this.snackBar.open('Error starting parser', 'Close', {
          duration: 3000,
        });
      },
    });
  }

  stopParsing(): void {
    this.parserService.stopParsing().subscribe({
      next: (response) => {
        this.snackBar.open(response.message, 'Close', { duration: 2000 });
        this.loadStatus();
      },
      error: (error) => {
        console.error('Error stopping parser:', error);
        this.snackBar.open('Error stopping parser', 'Close', {
          duration: 3000,
        });
      },
    });
  }

  parseAllGroups(): void {
    this.parserService.parseAllGroups().subscribe({
      next: (response) => {
        this.snackBar.open(response.message, 'Close', { duration: 2000 });
        this.loadStatus();
      },
      error: (error) => {
        console.error('Error parsing all groups:', error);
        this.snackBar.open('Error parsing all groups', 'Close', {
          duration: 3000,
        });
      },
    });
  }

  toggleGroupSelection(groupId: number): void {
    const index = this.selectedGroups.indexOf(groupId);
    if (index > -1) {
      this.selectedGroups.splice(index, 1);
    } else {
      this.selectedGroups.push(groupId);
    }
  }

  parseSelectedGroups(): void {
    if (this.selectedGroups.length === 0) {
      this.snackBar.open('Please select groups to parse', 'Close', {
        duration: 3000,
      });
      return;
    }

    this.parserService
      .startParsing({ group_ids: this.selectedGroups })
      .subscribe({
        next: (response) => {
          this.snackBar.open(response.message, 'Close', { duration: 2000 });
          this.loadStatus();
        },
        error: (error) => {
          console.error('Error parsing selected groups:', error);
          this.snackBar.open('Error parsing selected groups', 'Close', {
            duration: 3000,
          });
        },
      });
  }

  saveConfig(): void {
    const formValue = this.configForm.value;
    // Filter out null values and ensure proper types
    const config = {
      auto_parse_enabled: formValue.auto_parse_enabled ?? false,
      parse_interval_minutes: formValue.parse_interval_minutes ?? 30,
      max_posts_per_group: formValue.max_posts_per_group ?? 100,
      max_comments_per_post: formValue.max_comments_per_post ?? 100,
      parse_delay_seconds: formValue.parse_delay_seconds ?? 1,
    };

    this.parserService.updateParserConfig(config).subscribe({
      next: (updatedConfig) => {
        this.config = updatedConfig;
        this.snackBar.open('Configuration saved successfully', 'Close', {
          duration: 2000,
        });
      },
      error: (error) => {
        console.error('Error saving configuration:', error);
        this.snackBar.open('Error saving configuration', 'Close', {
          duration: 3000,
        });
      },
    });
  }

  clearLogs(): void {
    this.parserService.clearParserLogs().subscribe({
      next: (response) => {
        this.snackBar.open(response.message, 'Close', { duration: 2000 });
        this.loadLogs();
      },
      error: (error) => {
        console.error('Error clearing logs:', error);
        this.snackBar.open('Error clearing logs', 'Close', { duration: 3000 });
      },
    });
  }

  getLogLevelColor(level: string): string {
    switch (level) {
      case 'ERROR':
        return 'warn';
      case 'WARNING':
        return 'accent';
      case 'INFO':
        return 'primary';
      default:
        return 'primary';
    }
  }
}
