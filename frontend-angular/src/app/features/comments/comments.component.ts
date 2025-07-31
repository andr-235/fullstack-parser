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
  templateUrl: './comments.component.html',
  styleUrls: ['./comments.component.scss'],
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
