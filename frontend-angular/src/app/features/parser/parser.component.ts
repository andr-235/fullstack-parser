import {
  Component,
  inject,
  signal,
  computed,
  OnInit,
  OnDestroy,
  ChangeDetectionStrategy,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
} from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatListModule } from '@angular/material/list';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { Subject, interval } from 'rxjs';
import { takeUntil, catchError, finalize } from 'rxjs/operators';

import {
  ParserService,
  VKGroup,
  ParsingStats,
  ParseTaskCreate,
  ParseTaskResponse,
  ParseTaskStatus,
} from '../../core/services/parser.service';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';

interface ParserState {
  parsingStats: ParsingStats | null;
  groups: VKGroup[];
  selectedGroups: string[];
  tasks: ParseTaskResponse[];
  activeTaskId: string | null;
  loading: boolean;
  error: string | null;
}

@Component({
  selector: 'app-parser',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatCheckboxModule,
    MatProgressBarModule,
    MatChipsModule,
    MatExpansionModule,
    MatListModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    LoadingSpinnerComponent,
  ],
  templateUrl: './parser.component.html',
  styleUrls: ['./parser.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ParserComponent implements OnInit, OnDestroy {
  private readonly parserService = inject(ParserService);
  private readonly snackBar = inject(MatSnackBar);
  private readonly fb = inject(FormBuilder);
  private readonly destroy$ = new Subject<void>();

  // Private state signal
  private readonly _state = signal<ParserState>({
    parsingStats: null,
    groups: [],
    selectedGroups: [],
    tasks: [],
    activeTaskId: null,
    loading: false,
    error: null,
  });

  // Readonly computed signals for template
  readonly parsingStats = computed(() => this._state().parsingStats);
  readonly groups = computed(() => this._state().groups);
  readonly selectedGroups = computed(() => this._state().selectedGroups);
  readonly tasks = computed(() => this._state().tasks);
  readonly activeTaskId = computed(() => this._state().activeTaskId);
  readonly isLoading = computed(() => this._state().loading);
  readonly hasError = computed(() => !!this._state().error);

  // Computed values
  readonly hasGroups = computed(() => this.groups().length > 0);
  readonly hasSelectedGroups = computed(() => this.selectedGroups().length > 0);
  readonly hasActiveTask = computed(() => this.activeTaskId() !== null);
  readonly activeTask = computed(() =>
    this.tasks().find((task) => task.id === this.activeTaskId())
  );

  // Form
  configForm: FormGroup;

  constructor() {
    this.configForm = this.fb.group({
      postsLimit: [
        100,
        [Validators.required, Validators.min(1), Validators.max(1000)],
      ],
      commentsLimit: [
        100,
        [Validators.required, Validators.min(1), Validators.max(1000)],
      ],
    });
  }

  ngOnInit(): void {
    this.loadParsingStats();
    this.loadGroups();
    this.loadTasks();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadParsingStats(): void {
    this.parserService
      .getParsingStats()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (stats) => {
          this._state.update((state) => ({ ...state, parsingStats: stats }));
        },
        error: (error) => {
          this.showError('Failed to load parsing statistics');
        },
      });
  }

  loadGroups(): void {
    this.parserService
      .getAllGroups()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (groups) => {
          this._state.update((state) => ({ ...state, groups }));
        },
        error: (error) => {
          this.showError('Failed to load groups');
        },
      });
  }

  loadTasks(): void {
    this.parserService
      .getAllParseTasks()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (tasks) => {
          this._state.update((state) => ({ ...state, tasks }));
        },
        error: (error) => {
          this.showError('Failed to load tasks');
        },
      });
  }

  createParseTask(): void {
    if (!this.hasSelectedGroups()) {
      this.showError('Please select at least one group');
      return;
    }

    if (this.configForm.invalid) {
      this.showError('Please check your configuration');
      return;
    }

    const taskData: ParseTaskCreate = {
      groupIds: this.selectedGroups(),
      postsLimit: this.configForm.get('postsLimit')?.value,
      commentsLimit: this.configForm.get('commentsLimit')?.value,
    };

    this._state.update((state) => ({ ...state, loading: true, error: null }));

    this.parserService
      .createParseTask(taskData)
      .pipe(
        takeUntil(this.destroy$),
        finalize(() => {
          this._state.update((state) => ({ ...state, loading: false }));
        })
      )
      .subscribe({
        next: (task) => {
          this._state.update((state) => ({
            ...state,
            activeTaskId: task.id,
            tasks: [task, ...state.tasks],
          }));
          this.showSuccess('Task created successfully');
          this.startTaskMonitoring(task.id);
        },
        error: (error) => {
          this.showError('Failed to create task');
        },
      });
  }

  startTaskMonitoring(taskId: string): void {
    // Poll task status every 2 seconds
    interval(2000)
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.parserService
          .getParseTaskStatus(taskId)
          .pipe(takeUntil(this.destroy$))
          .subscribe({
            next: (status) => {
              this._state.update((state) => ({
                ...state,
                tasks: state.tasks.map((task) =>
                  task.id === taskId ? { ...task, ...status } : task
                ),
              }));

              // Stop monitoring if task is completed or failed
              if (status.status === 'completed' || status.status === 'failed') {
                this._state.update((state) => ({
                  ...state,
                  activeTaskId: null,
                }));
                this.showSuccess(`Task ${status.status}`);
              }
            },
            error: (error) => {
              console.error('Failed to get task status:', error);
            },
          });
      });
  }

  cancelTask(taskId: string): void {
    this.parserService
      .cancelParseTask(taskId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this._state.update((state) => ({
            ...state,
            tasks: state.tasks.map((task) =>
              task.id === taskId
                ? { ...task, status: 'failed', error: 'Cancelled by user' }
                : task
            ),
            activeTaskId:
              state.activeTaskId === taskId ? null : state.activeTaskId,
          }));
          this.showSuccess('Task cancelled successfully');
        },
        error: (error) => {
          this.showError('Failed to cancel task');
        },
      });
  }

  toggleGroupSelection(groupId: string): void {
    this._state.update((state) => {
      const selectedGroups = state.selectedGroups.includes(groupId)
        ? state.selectedGroups.filter((id) => id !== groupId)
        : [...state.selectedGroups, groupId];

      return { ...state, selectedGroups };
    });
  }

  isGroupSelected(groupId: string): boolean {
    return this.selectedGroups().includes(groupId);
  }

  getTaskStatusColor(status: string): string {
    switch (status) {
      case 'pending':
        return 'primary';
      case 'running':
        return 'accent';
      case 'completed':
        return 'primary';
      case 'failed':
        return 'warn';
      default:
        return 'primary';
    }
  }

  getTaskStatusIcon(status: string): string {
    switch (status) {
      case 'pending':
        return 'schedule';
      case 'running':
        return 'play_arrow';
      case 'completed':
        return 'check_circle';
      case 'failed':
        return 'error';
      default:
        return 'help';
    }
  }

  formatDate(date: Date): string {
    return new Date(date).toLocaleString();
  }

  private showSuccess(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
    });
  }

  private showError(message: string): void {
    this._state.update((state) => ({ ...state, error: message }));
    this.snackBar.open(message, 'Close', {
      duration: 5000,
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
      panelClass: ['error-snackbar'],
    });
  }
}
