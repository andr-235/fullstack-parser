import {
  Component,
  OnInit,
  OnDestroy,
  ChangeDetectionStrategy,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormControl } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Subject, takeUntil, debounceTime, distinctUntilChanged } from 'rxjs';

import {
  GroupsService,
  GroupsSearchParams,
} from '../../core/services/groups.service';
import { VKGroupResponse } from '../../core/models';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-groups',
  template: `
    <div class="groups-container">
      <mat-card>
        <mat-card-header>
          <mat-card-title>VK Groups Management</mat-card-title>
          <mat-card-subtitle>Manage and monitor VK groups</mat-card-subtitle>
        </mat-card-header>

        <mat-card-content>
          <!-- Search and Filters -->
          <div class="filters-section">
            <mat-form-field appearance="outline" class="search-field">
              <mat-label>Search groups</mat-label>
              <input
                matInput
                [formControl]="searchControl"
                placeholder="Enter group name or screen name"
              />
              <mat-icon matSuffix>search</mat-icon>
            </mat-form-field>

            <mat-checkbox
              [formControl]="activeOnlyControl"
              class="active-filter"
            >
              Active groups only
            </mat-checkbox>
          </div>

          <!-- Loading State -->
          <div *ngIf="loading" class="loading-section">
            <app-loading-spinner
              message="Loading groups..."
            ></app-loading-spinner>
          </div>

          <!-- Groups Table -->
          <div *ngIf="!loading && groups.length > 0" class="table-section">
            <table mat-table [dataSource]="groups" matSort>
              <!-- Name Column -->
              <ng-container matColumnDef="name">
                <th mat-header-cell *matHeaderCellDef mat-sort-header>Name</th>
                <td mat-cell *matCellDef="let group">
                  <div class="group-info">
                    <div class="group-name">{{ group.name }}</div>
                    <div class="group-screen-name">
                      @{{ group.screen_name }}
                    </div>
                  </div>
                </td>
              </ng-container>

              <!-- Members Column -->
              <ng-container matColumnDef="members">
                <th mat-header-cell *matHeaderCellDef mat-sort-header>
                  Members
                </th>
                <td mat-cell *matCellDef="let group">
                  {{ group.members_count || 'N/A' }}
                </td>
              </ng-container>

              <!-- Comments Column -->
              <ng-container matColumnDef="comments">
                <th mat-header-cell *matHeaderCellDef mat-sort-header>
                  Comments
                </th>
                <td mat-cell *matCellDef="let group">
                  {{ group.total_comments_found }}
                </td>
              </ng-container>

              <!-- Status Column -->
              <ng-container matColumnDef="status">
                <th mat-header-cell *matHeaderCellDef>Status</th>
                <td mat-cell *matCellDef="let group">
                  <mat-chip
                    [color]="group.is_active ? 'accent' : 'warn'"
                    selected
                  >
                    {{ group.is_active ? 'Active' : 'Inactive' }}
                  </mat-chip>
                </td>
              </ng-container>

              <!-- Last Parsed Column -->
              <ng-container matColumnDef="lastParsed">
                <th mat-header-cell *matHeaderCellDef mat-sort-header>
                  Last Parsed
                </th>
                <td mat-cell *matCellDef="let group">
                  {{
                    group.last_parsed_at
                      ? (group.last_parsed_at | date : 'short')
                      : 'Never'
                  }}
                </td>
              </ng-container>

              <!-- Actions Column -->
              <ng-container matColumnDef="actions">
                <th mat-header-cell *matHeaderCellDef>Actions</th>
                <td mat-cell *matCellDef="let group">
                  <button mat-icon-button [matMenuTriggerFor]="menu">
                    <mat-icon>more_vert</mat-icon>
                  </button>
                  <mat-menu #menu="matMenu">
                    <button mat-menu-item (click)="refreshGroup(group.id)">
                      <mat-icon>refresh</mat-icon>
                      <span>Refresh Info</span>
                    </button>
                    <button
                      mat-menu-item
                      (click)="toggleGroupActive(group.id, !group.is_active)"
                    >
                      <mat-icon>{{
                        group.is_active ? 'pause' : 'play_arrow'
                      }}</mat-icon>
                      <span>{{
                        group.is_active ? 'Deactivate' : 'Activate'
                      }}</span>
                    </button>
                    <button
                      mat-menu-item
                      (click)="deleteGroup(group.id)"
                      class="delete-action"
                    >
                      <mat-icon>delete</mat-icon>
                      <span>Delete</span>
                    </button>
                  </mat-menu>
                </td>
              </ng-container>

              <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
              <tr mat-row *matRowDef="let row; columns: displayedColumns"></tr>
            </table>

            <!-- Pagination -->
            <mat-paginator
              [length]="totalItems"
              [pageSize]="pageSize"
              [pageIndex]="currentPage"
              [pageSizeOptions]="[10, 25, 50, 100]"
              (page)="onPageChange($event)"
            >
            </mat-paginator>
          </div>

          <!-- Empty State -->
          <div *ngIf="!loading && groups.length === 0" class="empty-state">
            <mat-icon>group</mat-icon>
            <h3>No groups found</h3>
            <p>Try adjusting your search criteria or add a new group.</p>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [
    `
      .groups-container {
        padding: 20px;
        max-width: 1400px;
        margin: 0 auto;
      }

      .filters-section {
        display: flex;
        gap: 20px;
        align-items: center;
        margin-bottom: 20px;
        flex-wrap: wrap;
      }

      .search-field {
        flex: 1;
        min-width: 300px;
      }

      .active-filter {
        margin-left: 20px;
      }

      .loading-section {
        display: flex;
        justify-content: center;
        padding: 40px;
      }

      .table-section {
        margin-top: 20px;
      }

      .group-info {
        display: flex;
        flex-direction: column;
      }

      .group-name {
        font-weight: 500;
      }

      .group-screen-name {
        font-size: 0.875rem;
        color: #666;
      }

      .empty-state {
        text-align: center;
        padding: 40px;
        color: #666;
      }

      .empty-state mat-icon {
        font-size: 48px;
        width: 48px;
        height: 48px;
        margin-bottom: 16px;
      }

      .delete-action {
        color: #f44336;
      }

      table {
        width: 100%;
      }

      .mat-column-actions {
        width: 80px;
      }

      .mat-column-status {
        width: 120px;
      }

      .mat-column-members,
      .mat-column-comments {
        width: 100px;
      }
    `,
  ],
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatCheckboxModule,
    MatIconModule,
    MatPaginatorModule,
    MatSortModule,
    MatCardModule,
    MatChipsModule,
    MatTooltipModule,
    MatMenuModule,
    MatDialogModule,
    LoadingSpinnerComponent,
  ],
})
export class GroupsComponent implements OnInit, OnDestroy {
  groups: VKGroupResponse[] = [];
  loading = false;
  totalItems = 0;
  currentPage = 0;
  pageSize = 25;
  displayedColumns = [
    'name',
    'members',
    'comments',
    'status',
    'lastParsed',
    'actions',
  ];

  searchControl = new FormControl('');
  activeOnlyControl = new FormControl(false);

  private destroy$ = new Subject<void>();

  constructor(
    private groupsService: GroupsService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.setupSearchSubscription();
    this.loadGroups();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private setupSearchSubscription(): void {
    this.searchControl.valueChanges
      .pipe(takeUntil(this.destroy$), debounceTime(500), distinctUntilChanged())
      .subscribe(() => {
        this.currentPage = 0;
        this.loadGroups();
      });

    this.activeOnlyControl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.currentPage = 0;
        this.loadGroups();
      });
  }

  private loadGroups(): void {
    this.loading = true;

    const params: GroupsSearchParams = {
      page: this.currentPage + 1,
      size: this.pageSize,
      search: this.searchControl.value || undefined,
      active_only: this.activeOnlyControl.value || undefined,
    };

    this.groupsService
      .getGroups(params)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.groups = response.items;
          this.totalItems = response.total;
          this.loading = false;
        },
        error: (error) => {
          console.error('Error loading groups:', error);
          this.snackBar.open('Error loading groups', 'Close', {
            duration: 3000,
          });
          this.loading = false;
        },
      });
  }

  onPageChange(event: PageEvent): void {
    this.currentPage = event.pageIndex;
    this.pageSize = event.pageSize;
    this.loadGroups();
  }

  refreshGroup(groupId: number): void {
    this.groupsService
      .refreshGroupInfo(groupId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.snackBar.open('Group info refreshed', 'Close', {
            duration: 2000,
          });
          this.loadGroups();
        },
        error: (error) => {
          console.error('Error refreshing group:', error);
          this.snackBar.open('Error refreshing group', 'Close', {
            duration: 3000,
          });
        },
      });
  }

  toggleGroupActive(groupId: number, isActive: boolean): void {
    this.groupsService
      .toggleGroupActive(groupId, isActive)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.snackBar.open(
            `Group ${isActive ? 'activated' : 'deactivated'}`,
            'Close',
            { duration: 2000 }
          );
          this.loadGroups();
        },
        error: (error) => {
          console.error('Error toggling group status:', error);
          this.snackBar.open('Error updating group status', 'Close', {
            duration: 3000,
          });
        },
      });
  }

  deleteGroup(groupId: number): void {
    if (confirm('Are you sure you want to delete this group?')) {
      this.groupsService
        .deleteGroup(groupId)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: () => {
            this.snackBar.open('Group deleted', 'Close', { duration: 2000 });
            this.loadGroups();
          },
          error: (error) => {
            console.error('Error deleting group:', error);
            this.snackBar.open('Error deleting group', 'Close', {
              duration: 3000,
            });
          },
        });
    }
  }
}
