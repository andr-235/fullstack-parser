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
import { ReactiveFormsModule, FormControl } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialogModule } from '@angular/material/dialog';
import {
  debounceTime,
  distinctUntilChanged,
  Subject,
  takeUntil,
  catchError,
  finalize,
} from 'rxjs';

import {
  GroupsService,
  VKGroupResponse,
  GroupsQueryParams,
} from '../../core/services/groups.service';

interface GroupsState {
  items: VKGroupResponse[];
  total: number;
  page: number;
  size: number;
  loading: boolean;
  error: string | null;
  sortField: string | null;
  sortDirection: 'asc' | 'desc' | null;
}

@Component({
  selector: 'app-groups',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatCheckboxModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatCardModule,
    MatChipsModule,
    MatTooltipModule,
    MatDialogModule,
  ],
  templateUrl: './groups.component.html',
  styleUrls: ['./groups.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class GroupsComponent implements OnInit, OnDestroy {
  private readonly groupsService = inject(GroupsService);
  private readonly snackBar = inject(MatSnackBar);

  // Signals for state management
  private readonly _state = signal<GroupsState>({
    items: [],
    total: 0,
    page: 0,
    size: 25,
    loading: false,
    error: null,
    sortField: null,
    sortDirection: null,
  });

  // Readonly signals for template
  readonly groupsData = computed(() => this._state().items);
  readonly totalGroups = computed(() => this._state().total);
  readonly currentPage = computed(() => this._state().page);
  readonly pageSize = computed(() => this._state().size);
  readonly loading = computed(() => this._state().loading);
  readonly hasError = computed(() => !!this._state().error);
  readonly error = computed(() => this._state().error);
  readonly isEmpty = computed(
    () => !this.loading() && this.groupsData().length === 0
  );

  // Form controls
  readonly searchControl = new FormControl('');
  readonly activeOnlyControl = new FormControl(false);

  // Pagination options
  readonly pageSizeOptions = [10, 25, 50, 100];

  // Table columns
  readonly displayedColumns = signal([
    'name',
    'postCount',
    'status',
    'last_parsed',
    'actions',
  ]);

  // Private properties
  private readonly destroy$ = new Subject<void>();
  private readonly loadingActions = signal<Set<string>>(new Set());

  constructor() {
    // Setup search debouncing
    this.searchControl.valueChanges
      .pipe(debounceTime(300), distinctUntilChanged(), takeUntil(this.destroy$))
      .subscribe(() => {
        this.loadGroups();
      });

    // Setup active filter
    this.activeOnlyControl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.loadGroups();
      });
  }

  ngOnInit(): void {
    this.loadGroups();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onPageChange(event: PageEvent): void {
    this._state.update((state: GroupsState) => ({
      ...state,
      page: event.pageIndex,
      size: event.pageSize,
    }));
    this.loadGroups();
  }

  onSortChange(sort: Sort): void {
    this._state.update((state: GroupsState) => ({
      ...state,
      sortField: sort.active || null,
      sortDirection: sort.direction || null,
    }));
    this.loadGroups();
  }

  refreshGroupInfo(groupId: string): void {
    this.setActionLoading(groupId, true);

    this.groupsService
      .getGroup(groupId)
      .pipe(
        takeUntil(this.destroy$),
        catchError((error: any) => {
          this.showError('Не удалось обновить информацию о группе');
          throw error;
        }),
        finalize(() => this.setActionLoading(groupId, false))
      )
      .subscribe(() => {
        this.showSuccess('Информация о группе успешно обновлена');
        this.loadGroups(); // Reload the list
      });
  }

  toggleGroupActive(group: VKGroupResponse): void {
    const newStatus = !group.isActive;
    this.setActionLoading(group.id, true);

    this.groupsService
      .toggleGroupActive(group.id, newStatus)
      .pipe(
        takeUntil(this.destroy$),
        catchError((error: any) => {
          this.showError(
            `Не удалось ${newStatus ? 'активировать' : 'деактивировать'} группу`
          );
          throw error;
        }),
        finalize(() => this.setActionLoading(group.id, false))
      )
      .subscribe(() => {
        this.showSuccess(
          `Группа успешно ${newStatus ? 'активирована' : 'деактивирована'}`
        );
        this.loadGroups(); // Reload the list
      });
  }

  deleteGroup(group: VKGroupResponse): void {
    if (confirm(`Вы уверены, что хотите удалить группу "${group.name}"?`)) {
      this.setActionLoading(group.id, true);

      this.groupsService
        .deleteGroup(group.id)
        .pipe(
          takeUntil(this.destroy$),
          catchError((error: any) => {
            this.showError('Не удалось удалить группу');
            throw error;
          }),
          finalize(() => this.setActionLoading(group.id, false))
        )
        .subscribe(() => {
          this.showSuccess('Группа успешно удалена');
          this.loadGroups(); // Reload the list
        });
    }
  }

  isActionLoading(groupId: string): boolean {
    return this.loadingActions().has(groupId);
  }

  private setActionLoading(groupId: string, loading: boolean): void {
    this.loadingActions.update((actions: Set<string>) => {
      const newActions = new Set(actions);
      if (loading) {
        newActions.add(groupId);
      } else {
        newActions.delete(groupId);
      }
      return newActions;
    });
  }

  private loadGroups(): void {
    this._state.update((state) => ({ ...state, loading: true, error: null }));

    const params: GroupsQueryParams = {
      page: this.currentPage() + 1, // Backend uses 1-based pagination
      limit: this.pageSize(),
      search: this.searchControl.value || undefined,
      isActive: this.activeOnlyControl.value || undefined,
    };

    this.groupsService
      .getGroups(params)
      .pipe(
        takeUntil(this.destroy$),
        catchError((error) => {
          console.error('Error loading groups:', error);
          this._state.update((state) => ({
            ...state,
            loading: false,
            error: error.message || 'Не удалось загрузить группы',
          }));
          this.showError('Не удалось загрузить группы');
          throw error;
        }),
        finalize(() => {
          this._state.update((state) => ({ ...state, loading: false }));
        })
      )
      .subscribe((response) => {
        this._state.update((state: GroupsState) => ({
          ...state,
          items: response.groups,
          total: response.total,
          loading: false,
        }));
      });
  }

  private showSuccess(message: string): void {
    this.snackBar.open(message, 'Закрыть', {
      duration: 3000,
      horizontalPosition: 'end',
      verticalPosition: 'top',
    });
  }

  private showError(message: string): void {
    this.snackBar.open(message, 'Закрыть', {
      duration: 5000,
      horizontalPosition: 'end',
      verticalPosition: 'top',
      panelClass: ['error-snackbar'],
    });
  }
}
