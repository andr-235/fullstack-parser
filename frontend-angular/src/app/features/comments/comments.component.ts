import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormControl, FormGroup } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatExpansionModule } from '@angular/material/expansion';
import { Subject, takeUntil, debounceTime, distinctUntilChanged } from 'rxjs';

import { CommentsService } from '../../core/services/comments.service';
import { GroupsService } from '../../core/services/groups.service';
import { KeywordsService } from '../../core/services/keywords.service';
import {
  VKCommentResponse,
  CommentSearchParams,
  VKGroupResponse,
  KeywordResponse,
} from '../../core/models';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-comments',
  template: `
    <div class="comments-container">
      <mat-card>
        <mat-card-header>
          <mat-card-title>Comments Management</mat-card-title>
          <mat-card-subtitle
            >Search and manage VK comments with keyword
            matches</mat-card-subtitle
          >
        </mat-card-header>

        <mat-card-content>
          <!-- Advanced Search and Filters -->
          <mat-expansion-panel class="filters-panel">
            <mat-expansion-panel-header>
              <mat-panel-title>
                <mat-icon>filter_list</mat-icon>
                Search & Filters
              </mat-panel-title>
            </mat-expansion-panel-header>

            <div class="filters-section">
              <!-- Text Search -->
              <mat-form-field appearance="outline" class="search-field">
                <mat-label>Search comments</mat-label>
                <input
                  matInput
                  [formControl]="textControl"
                  placeholder="Enter comment text to search"
                />
                <mat-icon matSuffix>search</mat-icon>
              </mat-form-field>

              <!-- Group Filter -->
              <mat-form-field appearance="outline" class="group-field">
                <mat-label>Group</mat-label>
                <mat-select [formControl]="groupIdControl">
                  <mat-option value="">All groups</mat-option>
                  <mat-option *ngFor="let group of groups" [value]="group.id">
                    {{ group.name }}
                  </mat-option>
                </mat-select>
              </mat-form-field>

              <!-- Keyword Filter -->
              <mat-form-field appearance="outline" class="keyword-field">
                <mat-label>Keyword</mat-label>
                <mat-select [formControl]="keywordIdControl">
                  <mat-option value="">All keywords</mat-option>
                  <mat-option
                    *ngFor="let keyword of keywords"
                    [value]="keyword.id"
                  >
                    {{ keyword.word }}
                  </mat-option>
                </mat-select>
              </mat-form-field>

              <!-- Date Range -->
              <div class="date-range">
                <mat-form-field appearance="outline">
                  <mat-label>From Date</mat-label>
                  <input
                    matInput
                    [matDatepicker]="fromPicker"
                    [formControl]="dateFromControl"
                  />
                  <mat-datepicker-toggle
                    matSuffix
                    [for]="fromPicker"
                  ></mat-datepicker-toggle>
                  <mat-datepicker #fromPicker></mat-datepicker>
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>To Date</mat-label>
                  <input
                    matInput
                    [matDatepicker]="toPicker"
                    [formControl]="dateToControl"
                  />
                  <mat-datepicker-toggle
                    matSuffix
                    [for]="toPicker"
                  ></mat-datepicker-toggle>
                  <mat-datepicker #toPicker></mat-datepicker>
                </mat-form-field>
              </div>

              <!-- Status Filters -->
              <div class="status-filters">
                <mat-checkbox
                  [formControl]="isViewedControl"
                  class="status-filter"
                >
                  Viewed only
                </mat-checkbox>
                <mat-checkbox
                  [formControl]="isArchivedControl"
                  class="status-filter"
                >
                  Archived only
                </mat-checkbox>
              </div>

              <!-- Sort Options -->
              <div class="sort-options">
                <mat-form-field appearance="outline" class="sort-field">
                  <mat-label>Sort by</mat-label>
                  <mat-select [formControl]="orderByControl">
                    <mat-option value="published_at">Date</mat-option>
                    <mat-option value="likes_count">Likes</mat-option>
                    <mat-option value="matched_keywords_count"
                      >Keyword Matches</mat-option
                    >
                    <mat-option value="author_screen_name">Author</mat-option>
                  </mat-select>
                </mat-form-field>

                <mat-form-field appearance="outline" class="sort-field">
                  <mat-label>Order</mat-label>
                  <mat-select [formControl]="orderDirControl">
                    <mat-option value="desc">Descending</mat-option>
                    <mat-option value="asc">Ascending</mat-option>
                  </mat-select>
                </mat-form-field>
              </div>
            </div>
          </mat-expansion-panel>

          <!-- Loading State -->
          <div *ngIf="loading" class="loading-section">
            <app-loading-spinner
              message="Loading comments..."
            ></app-loading-spinner>
          </div>

          <!-- Comments Table -->
          <div *ngIf="!loading && comments.length > 0" class="table-section">
            <div class="table-actions">
              <button
                mat-raised-button
                color="primary"
                (click)="exportComments()"
              >
                <mat-icon>download</mat-icon>
                Export
              </button>
              <button
                mat-raised-button
                color="accent"
                (click)="bulkMarkViewed()"
              >
                <mat-icon>visibility</mat-icon>
                Mark Viewed
              </button>
              <button mat-raised-button color="warn" (click)="bulkArchive()">
                <mat-icon>archive</mat-icon>
                Archive
              </button>
            </div>

            <table mat-table [dataSource]="comments" matSort>
              <!-- Selection Column -->
              <ng-container matColumnDef="select">
                <th mat-header-cell *matHeaderCellDef>
                  <mat-checkbox
                    (change)="$event ? masterToggle() : null"
                    [checked]="selection.hasValue() && isAllSelected()"
                    [indeterminate]="selection.hasValue() && !isAllSelected()"
                  >
                  </mat-checkbox>
                </th>
                <td mat-cell *matCellDef="let row">
                  <mat-checkbox
                    (click)="$event.stopPropagation()"
                    (change)="$event ? selection.toggle(row) : null"
                    [checked]="selection.isSelected(row)"
                  >
                  </mat-checkbox>
                </td>
              </ng-container>

              <!-- Text Column -->
              <ng-container matColumnDef="text">
                <th mat-header-cell *matHeaderCellDef mat-sort-header>
                  Comment
                </th>
                <td mat-cell *matCellDef="let comment">
                  <div class="comment-content">
                    <div class="comment-text">{{ comment.text }}</div>
                    <div class="comment-meta">
                      <span class="author"
                        >@{{
                          comment.author_screen_name || comment.author_id
                        }}</span
                      >
                      <span class="date">{{
                        comment.published_at | date : 'short'
                      }}</span>
                      <span class="likes">❤️ {{ comment.likes_count }}</span>
                    </div>
                  </div>
                </td>
              </ng-container>

              <!-- Group Column -->
              <ng-container matColumnDef="group">
                <th mat-header-cell *matHeaderCellDef mat-sort-header>Group</th>
                <td mat-cell *matCellDef="let comment">
                  <div class="group-info" *ngIf="comment.group">
                    <div class="group-name">{{ comment.group.name }}</div>
                    <div class="group-screen">
                      @{{ comment.group.screen_name }}
                    </div>
                  </div>
                </td>
              </ng-container>

              <!-- Keywords Column -->
              <ng-container matColumnDef="keywords">
                <th mat-header-cell *matHeaderCellDef mat-sort-header>
                  Keywords
                </th>
                <td mat-cell *matCellDef="let comment">
                  <div
                    class="keywords-chips"
                    *ngIf="
                      comment.matched_keywords &&
                      comment.matched_keywords.length > 0
                    "
                  >
                    <mat-chip
                      *ngFor="let keyword of comment.matched_keywords"
                      size="small"
                      color="accent"
                    >
                      {{ keyword }}
                    </mat-chip>
                  </div>
                  <span
                    *ngIf="
                      !comment.matched_keywords ||
                      comment.matched_keywords.length === 0
                    "
                    >-</span
                  >
                </td>
              </ng-container>

              <!-- Status Column -->
              <ng-container matColumnDef="status">
                <th mat-header-cell *matHeaderCellDef>Status</th>
                <td mat-cell *matCellDef="let comment">
                  <div class="status-chips">
                    <mat-chip
                      *ngIf="comment.is_viewed"
                      size="small"
                      color="primary"
                    >
                      Viewed
                    </mat-chip>
                    <mat-chip
                      *ngIf="comment.is_archived"
                      size="small"
                      color="warn"
                    >
                      Archived
                    </mat-chip>
                    <mat-chip
                      *ngIf="!comment.is_viewed && !comment.is_archived"
                      size="small"
                      color="accent"
                    >
                      New
                    </mat-chip>
                  </div>
                </td>
              </ng-container>

              <!-- Actions Column -->
              <ng-container matColumnDef="actions">
                <th mat-header-cell *matHeaderCellDef>Actions</th>
                <td mat-cell *matCellDef="let comment">
                  <button mat-icon-button [matMenuTriggerFor]="menu">
                    <mat-icon>more_vert</mat-icon>
                  </button>
                  <mat-menu #menu="matMenu">
                    <button mat-menu-item (click)="viewComment(comment)">
                      <mat-icon>visibility</mat-icon>
                      <span>View Details</span>
                    </button>
                    <button
                      mat-menu-item
                      (click)="markAsViewed(comment.id)"
                      *ngIf="!comment.is_viewed"
                    >
                      <mat-icon>visibility</mat-icon>
                      <span>Mark Viewed</span>
                    </button>
                    <button
                      mat-menu-item
                      (click)="markAsArchived(comment.id)"
                      *ngIf="!comment.is_archived"
                    >
                      <mat-icon>archive</mat-icon>
                      <span>Archive</span>
                    </button>
                    <button
                      mat-menu-item
                      (click)="deleteComment(comment.id)"
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
          <div *ngIf="!loading && comments.length === 0" class="empty-state">
            <mat-icon>comment</mat-icon>
            <h3>No comments found</h3>
            <p>
              Try adjusting your search criteria or check if there are any
              comments in the system.
            </p>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [
    `
      .comments-container {
        padding: 20px;
        max-width: 1600px;
        margin: 0 auto;
      }

      .filters-panel {
        margin-bottom: 20px;
      }

      .filters-section {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin-top: 20px;
      }

      .search-field {
        grid-column: 1 / -1;
      }

      .date-range {
        display: flex;
        gap: 10px;
        grid-column: 1 / -1;
      }

      .status-filters {
        display: flex;
        gap: 20px;
        grid-column: 1 / -1;
      }

      .sort-options {
        display: flex;
        gap: 10px;
        grid-column: 1 / -1;
      }

      .sort-field {
        min-width: 150px;
      }

      .loading-section {
        display: flex;
        justify-content: center;
        padding: 40px;
      }

      .table-section {
        margin-top: 20px;
      }

      .table-actions {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        flex-wrap: wrap;
      }

      .comment-content {
        display: flex;
        flex-direction: column;
        gap: 4px;
      }

      .comment-text {
        font-weight: 500;
        line-height: 1.4;
      }

      .comment-meta {
        display: flex;
        gap: 10px;
        font-size: 0.875rem;
        color: #666;
      }

      .group-info {
        display: flex;
        flex-direction: column;
      }

      .group-name {
        font-weight: 500;
      }

      .group-screen {
        font-size: 0.875rem;
        color: #666;
      }

      .keywords-chips {
        display: flex;
        gap: 4px;
        flex-wrap: wrap;
      }

      .status-chips {
        display: flex;
        gap: 4px;
        flex-wrap: wrap;
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

      .mat-column-select {
        width: 50px;
      }

      .mat-column-actions {
        width: 80px;
      }

      .mat-column-status {
        width: 120px;
      }

      .mat-column-keywords {
        width: 150px;
      }

      .mat-column-group {
        width: 150px;
      }
    `,
  ],
  standalone: true,
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
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatExpansionModule,
    LoadingSpinnerComponent,
  ],
})
export class CommentsComponent implements OnInit, OnDestroy {
  comments: VKCommentResponse[] = [];
  groups: VKGroupResponse[] = [];
  keywords: KeywordResponse[] = [];
  loading = false;
  totalItems = 0;
  currentPage = 0;
  pageSize = 25;
  displayedColumns = [
    'select',
    'text',
    'group',
    'keywords',
    'status',
    'actions',
  ];

  searchForm = new FormGroup({
    text: new FormControl(''),
    group_id: new FormControl(''),
    keyword_id: new FormControl(''),
    date_from: new FormControl(''),
    date_to: new FormControl(''),
    is_viewed: new FormControl(false),
    is_archived: new FormControl(false),
    order_by: new FormControl('published_at'),
    order_dir: new FormControl('desc'),
  });

  // Getters for form controls
  get textControl() {
    return this.searchForm.get('text') as FormControl;
  }
  get groupIdControl() {
    return this.searchForm.get('group_id') as FormControl;
  }
  get keywordIdControl() {
    return this.searchForm.get('keyword_id') as FormControl;
  }
  get dateFromControl() {
    return this.searchForm.get('date_from') as FormControl;
  }
  get dateToControl() {
    return this.searchForm.get('date_to') as FormControl;
  }
  get isViewedControl() {
    return this.searchForm.get('is_viewed') as FormControl;
  }
  get isArchivedControl() {
    return this.searchForm.get('is_archived') as FormControl;
  }
  get orderByControl() {
    return this.searchForm.get('order_by') as FormControl;
  }
  get orderDirControl() {
    return this.searchForm.get('order_dir') as FormControl;
  }

  selection = new SelectionModel<VKCommentResponse>(true, []);

  private destroy$ = new Subject<void>();

  constructor(
    private commentsService: CommentsService,
    private groupsService: GroupsService,
    private keywordsService: KeywordsService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.setupSearchSubscription();
    this.loadGroups();
    this.loadKeywords();
    this.loadComments();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private setupSearchSubscription(): void {
    this.searchForm.valueChanges
      .pipe(takeUntil(this.destroy$), debounceTime(500), distinctUntilChanged())
      .subscribe(() => {
        this.currentPage = 0;
        this.loadComments();
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

  private loadKeywords(): void {
    this.keywordsService.getKeywords({ size: 100 }).subscribe({
      next: (response) => {
        this.keywords = response.items;
      },
      error: (error) => {
        console.error('Error loading keywords:', error);
      },
    });
  }

  private loadComments(): void {
    this.loading = true;

    const formValue = this.searchForm.value;
    const params: CommentSearchParams = {
      text: formValue.text || undefined,
      group_id: formValue.group_id ? Number(formValue.group_id) : undefined,
      keyword_id: formValue.keyword_id
        ? Number(formValue.keyword_id)
        : undefined,
      date_from: formValue.date_from || undefined,
      date_to: formValue.date_to || undefined,
      is_viewed: formValue.is_viewed || undefined,
      is_archived: formValue.is_archived || undefined,
      order_by: formValue.order_by || undefined,
      order_dir: formValue.order_dir || undefined,
    };

    this.commentsService.getComments(params).subscribe({
      next: (response) => {
        this.comments = response.items;
        this.totalItems = response.total;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading comments:', error);
        this.snackBar.open('Error loading comments', 'Close', {
          duration: 3000,
        });
        this.loading = false;
      },
    });
  }

  onPageChange(event: PageEvent): void {
    this.currentPage = event.pageIndex;
    this.pageSize = event.pageSize;
    this.loadComments();
  }

  // Selection methods
  isAllSelected(): boolean {
    const numSelected = this.selection.selected.length;
    const numRows = this.comments.length;
    return numSelected === numRows;
  }

  masterToggle(): void {
    this.isAllSelected()
      ? this.selection.clear()
      : this.comments.forEach((row) => this.selection.select(row));
  }

  // Action methods
  viewComment(comment: VKCommentResponse): void {
    // TODO: Implement comment detail dialog
    console.log('View comment:', comment);
  }

  markAsViewed(commentId: number): void {
    this.commentsService.markAsViewed(commentId).subscribe({
      next: () => {
        this.snackBar.open('Comment marked as viewed', 'Close', {
          duration: 2000,
        });
        this.loadComments();
      },
      error: (error) => {
        console.error('Error marking comment as viewed:', error);
        this.snackBar.open('Error marking comment as viewed', 'Close', {
          duration: 3000,
        });
      },
    });
  }

  markAsArchived(commentId: number): void {
    this.commentsService.markAsArchived(commentId).subscribe({
      next: () => {
        this.snackBar.open('Comment archived', 'Close', { duration: 2000 });
        this.loadComments();
      },
      error: (error) => {
        console.error('Error archiving comment:', error);
        this.snackBar.open('Error archiving comment', 'Close', {
          duration: 3000,
        });
      },
    });
  }

  deleteComment(commentId: number): void {
    if (confirm('Are you sure you want to delete this comment?')) {
      this.commentsService.deleteComment(commentId).subscribe({
        next: () => {
          this.snackBar.open('Comment deleted', 'Close', { duration: 2000 });
          this.loadComments();
        },
        error: (error) => {
          console.error('Error deleting comment:', error);
          this.snackBar.open('Error deleting comment', 'Close', {
            duration: 3000,
          });
        },
      });
    }
  }

  bulkMarkViewed(): void {
    const selectedIds = this.selection.selected.map((comment) => comment.id);
    if (selectedIds.length === 0) {
      this.snackBar.open('Please select comments to mark as viewed', 'Close', {
        duration: 3000,
      });
      return;
    }

    this.commentsService
      .bulkUpdate(selectedIds, { is_viewed: true })
      .subscribe({
        next: () => {
          this.snackBar.open(
            `${selectedIds.length} comments marked as viewed`,
            'Close',
            { duration: 2000 }
          );
          this.selection.clear();
          this.loadComments();
        },
        error: (error) => {
          console.error('Error bulk marking comments as viewed:', error);
          this.snackBar.open('Error marking comments as viewed', 'Close', {
            duration: 3000,
          });
        },
      });
  }

  bulkArchive(): void {
    const selectedIds = this.selection.selected.map((comment) => comment.id);
    if (selectedIds.length === 0) {
      this.snackBar.open('Please select comments to archive', 'Close', {
        duration: 3000,
      });
      return;
    }

    this.commentsService
      .bulkUpdate(selectedIds, { is_archived: true })
      .subscribe({
        next: () => {
          this.snackBar.open(
            `${selectedIds.length} comments archived`,
            'Close',
            { duration: 2000 }
          );
          this.selection.clear();
          this.loadComments();
        },
        error: (error) => {
          console.error('Error bulk archiving comments:', error);
          this.snackBar.open('Error archiving comments', 'Close', {
            duration: 3000,
          });
        },
      });
  }

  exportComments(): void {
    const formValue = this.searchForm.value;
    const params: CommentSearchParams = {
      text: formValue.text || undefined,
      group_id: formValue.group_id ? Number(formValue.group_id) : undefined,
      keyword_id: formValue.keyword_id
        ? Number(formValue.keyword_id)
        : undefined,
      date_from: formValue.date_from || undefined,
      date_to: formValue.date_to || undefined,
      is_viewed: formValue.is_viewed || undefined,
      is_archived: formValue.is_archived || undefined,
      order_by: formValue.order_by || undefined,
      order_dir: formValue.order_dir || undefined,
    };

    this.commentsService.exportComments(params).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `comments_export_${
          new Date().toISOString().split('T')[0]
        }.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
        this.snackBar.open('Comments exported successfully', 'Close', {
          duration: 2000,
        });
      },
      error: (error) => {
        console.error('Error exporting comments:', error);
        this.snackBar.open('Error exporting comments', 'Close', {
          duration: 3000,
        });
      },
    });
  }
}

// SelectionModel class for table selection
class SelectionModel<T> {
  private _selection = new Set<T>();

  constructor(private _multiple = false, initiallySelectedValues?: T[]) {
    if (initiallySelectedValues) {
      initiallySelectedValues.forEach((value) => this._selection.add(value));
    }
  }

  get selected(): T[] {
    return Array.from(this._selection);
  }

  select(...values: T[]): void {
    values.forEach((value) => this._selection.add(value));
  }

  deselect(...values: T[]): void {
    values.forEach((value) => this._selection.delete(value));
  }

  toggle(value: T): void {
    if (this.isSelected(value)) {
      this.deselect(value);
    } else {
      this.select(value);
    }
  }

  clear(): void {
    this._selection.clear();
  }

  isSelected(value: T): boolean {
    return this._selection.has(value);
  }

  hasValue(): boolean {
    return this._selection.size > 0;
  }
}
