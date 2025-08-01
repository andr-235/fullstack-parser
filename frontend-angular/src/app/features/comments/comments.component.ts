import {
  Component,
  computed,
  signal,
  input,
  output,
  inject,
  OnInit,
  OnDestroy,
  ChangeDetectorRef,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormControl } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { SelectionModel } from '@angular/cdk/collections';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil } from 'rxjs/operators';
import { ChangeDetectionStrategy } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { CommentsService } from '../../core/services/comments.service';
import {
  GroupsService,
  VKGroupResponse,
} from '../../core/services/groups.service';
import { KeywordsService } from '../../core/services/keywords.service';
import { VKCommentResponse } from '../../core/models/vk-comment.model';

// Interfaces
interface Comment {
  id: string;
  text: string;
  author_screen_name: string;
  published_at: string;
  likes_count: number;
  group_name: string;
  group_screen_name: string;
  keywords: string[];
  is_viewed: boolean;
  is_archived: boolean;
}

interface Group {
  id: string;
  name: string;
  screen_name: string;
}

interface Keyword {
  id: string;
  word: string;
}

interface CommentsResponse {
  comments: Comment[];
  total: number;
}

@Component({
  selector: 'app-comments',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCheckboxModule,
    MatTableModule,
    MatSortModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatMenuModule,
    MatTooltipModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatIconModule,
    MatButtonModule,
  ],
  templateUrl: './comments.component.html',
  styleUrls: ['./comments.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommentsComponent implements OnInit, OnDestroy {
  // Inputs
  initialFilters = input<Partial<any>>({});

  // Outputs
  commentDeleted = output<string>();
  commentViewed = output<string>();
  commentArchived = output<string>();

  // Dependencies
  private readonly commentsService = inject(CommentsService);
  private readonly groupsService = inject(GroupsService);
  private readonly keywordsService = inject(KeywordsService);
  private readonly snackBar = inject(MatSnackBar);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly sanitizer = inject(DomSanitizer);
  private readonly destroy$ = new Subject<void>();

  // API endpoints
  private readonly apiUrl = environment.apiUrl;

  // Signals
  commentsData = signal<Comment[]>([]);
  groupsData = signal<Group[]>([]);
  keywordsData = signal<Keyword[]>([]);
  isLoading = signal(false);
  error = signal('');
  currentPageIndex = signal(0);
  pageSizeValue = signal(25);
  totalItemsCount = signal(0);
  actionLoadingIds = signal<Set<string>>(new Set());

  // Selection model for checkboxes
  selection = new SelectionModel<Comment>(true, []);

  // Form controls
  textControl = new FormControl('');
  groupIdControl = new FormControl('');
  keywordIdControl = new FormControl('');
  dateFromControl = new FormControl<Date | null>(null);
  dateToControl = new FormControl<Date | null>(null);
  isViewedControl = new FormControl(false);
  isArchivedControl = new FormControl(false);
  orderByControl = new FormControl('published_at');
  orderDirControl = new FormControl('desc');

  // Computed values
  displayedColumns = computed(() => [
    'select',
    'text',
    'group',
    'status',
    'actions',
  ]);

  ngOnInit(): void {
    this.setupFormListeners();

    // Add a small delay to prevent race conditions during component initialization
    setTimeout(() => {
      this.loadGroups();
      this.loadKeywords();
      this.loadComments();
    }, 100);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  highlightKeywords(text: string, keywords: string[]): SafeHtml {
    if (!keywords || keywords.length === 0) {
      return this.sanitizer.bypassSecurityTrustHtml(text);
    }

    let highlightedText = text;

    // Сортируем ключевые слова по длине (от длинных к коротким), чтобы избежать проблем с вложенными совпадениями
    const sortedKeywords = [...keywords].sort((a, b) => b.length - a.length);

    for (const keyword of sortedKeywords) {
      const regex = new RegExp(
        `(${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`,
        'gi'
      );
      highlightedText = highlightedText.replace(
        regex,
        '<span class="highlighted-keyword">$1</span>'
      );
    }

    return this.sanitizer.bypassSecurityTrustHtml(highlightedText);
  }

  private setupFormListeners(): void {
    // Debounced text search
    this.textControl.valueChanges
      .pipe(debounceTime(300), distinctUntilChanged(), takeUntil(this.destroy$))
      .subscribe(() => {
        this.currentPageIndex.set(0);
        this.loadComments();
      });

    // Other filter changes
    this.groupIdControl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.currentPageIndex.set(0);
        this.loadComments();
      });

    this.keywordIdControl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.currentPageIndex.set(0);
        this.loadComments();
      });

    this.dateFromControl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.currentPageIndex.set(0);
        this.loadComments();
      });

    this.dateToControl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.currentPageIndex.set(0);
        this.loadComments();
      });

    this.isViewedControl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.currentPageIndex.set(0);
        this.loadComments();
      });

    this.isArchivedControl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.currentPageIndex.set(0);
        this.loadComments();
      });

    this.orderByControl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.currentPageIndex.set(0);
        this.loadComments();
      });

    this.orderDirControl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.currentPageIndex.set(0);
        this.loadComments();
      });
  }

  private loadGroups(): void {
    this.groupsService.getGroups().subscribe({
      next: (response) => {
        // Преобразуем VKGroupResponse в Group
        const groups: Group[] = (response.groups || []).map((group) => ({
          id: group.id,
          name: group.name,
          screen_name: group.screenName,
        }));
        this.groupsData.set(groups);
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error loading groups:', error);
        this.groupsData.set([]);
        this.cdr.markForCheck();
      },
    });
  }

  private loadKeywords(): void {
    this.keywordsService.getKeywords().subscribe({
      next: (response) => {
        // Преобразуем KeywordResponse в Keyword
        const keywords: Keyword[] = (response.items || []).map((keyword) => ({
          id: keyword.id.toString(),
          word: keyword.word,
        }));
        this.keywordsData.set(keywords);
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error loading keywords:', error);
        this.keywordsData.set([]);
        this.cdr.markForCheck();
      },
    });
  }

  private loadComments(): void {
    this.isLoading.set(true);
    this.error.set('');

    const params = {
      page: this.currentPageIndex() + 1,
      page_size: this.pageSizeValue(),
      search: this.textControl.value || undefined,
      group_id: this.groupIdControl.value
        ? parseInt(this.groupIdControl.value)
        : undefined,
      keyword_id: this.keywordIdControl.value
        ? parseInt(this.keywordIdControl.value)
        : undefined,
      date_from: this.dateFromControl.value?.toISOString(),
      date_to: this.dateToControl.value?.toISOString(),
      is_viewed: this.isViewedControl.value || undefined,
      is_archived: this.isArchivedControl.value || undefined,
      sort_by: this.orderByControl.value,
      sort_order: this.orderDirControl.value,
    };

    this.commentsService.getComments(params).subscribe({
      next: (response) => {
        // Преобразуем VKCommentResponse в Comment
        const comments: Comment[] = (response.items || []).map(
          (comment: any) => ({
            id: comment.id.toString(),
            text: comment.text,
            author_screen_name: comment.author_name || '',
            published_at: comment.date,
            likes_count: comment.likes_count,
            group_name: comment.group_name,
            group_screen_name: comment.group_name, // Используем group_name как screen_name
            keywords: comment.keywords || [],
            is_viewed: comment.is_viewed,
            is_archived: comment.is_archived,
          })
        );
        this.commentsData.set(comments);
        this.totalItemsCount.set(response.total || 0);
        this.isLoading.set(false);
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error loading comments:', error);
        this.error.set('Ошибка загрузки комментариев');
        this.commentsData.set([]);
        this.totalItemsCount.set(0);
        this.isLoading.set(false);
        this.cdr.markForCheck();
      },
    });
  }

  onSortChange(sort: Sort): void {
    this.orderByControl.setValue(sort.active);
    this.orderDirControl.setValue(sort.direction);
  }

  isActionLoading(id: string): boolean {
    return this.actionLoadingIds().has(id);
  }

  private setActionLoading(id: string, loading: boolean): void {
    const currentIds = new Set(this.actionLoadingIds());
    if (loading) {
      currentIds.add(id);
    } else {
      currentIds.delete(id);
    }
    this.actionLoadingIds.set(currentIds);
  }

  isAllSelected(): boolean {
    const numSelected = this.selection.selected.length;
    const numRows = this.commentsData().length;
    return numSelected === numRows;
  }

  masterToggle(): void {
    if (this.isAllSelected()) {
      this.selection.clear();
    } else {
      this.commentsData().forEach((row) => this.selection.select(row));
    }
  }

  viewComment(comment: Comment): void {
    // Implement view comment logic
    console.log('View comment:', comment);
  }

  markAsViewed(commentId: string): void {
    this.setActionLoading(commentId, true);
    this.commentsService.markAsViewed(parseInt(commentId)).subscribe({
      next: () => {
        this.commentViewed.emit(commentId);
        this.snackBar.open('Комментарий отмечен как просмотренный', 'Закрыть', {
          duration: 3000,
        });
        this.loadComments();
        this.setActionLoading(commentId, false);
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error marking comment as viewed:', error);
        this.snackBar.open('Ошибка при отметке комментария', 'Закрыть', {
          duration: 3000,
        });
        this.setActionLoading(commentId, false);
        this.cdr.markForCheck();
      },
    });
  }

  markAsArchived(commentId: string): void {
    this.setActionLoading(commentId, true);
    this.commentsService.markAsArchived(parseInt(commentId)).subscribe({
      next: () => {
        this.commentArchived.emit(commentId);
        this.snackBar.open('Комментарий архивирован', 'Закрыть', {
          duration: 3000,
        });
        this.loadComments();
        this.setActionLoading(commentId, false);
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error archiving comment:', error);
        this.snackBar.open('Ошибка при архивировании комментария', 'Закрыть', {
          duration: 3000,
        });
        this.setActionLoading(commentId, false);
        this.cdr.markForCheck();
      },
    });
  }

  deleteComment(commentId: string): void {
    this.setActionLoading(commentId, true);
    this.commentsService.deleteComment(parseInt(commentId)).subscribe({
      next: () => {
        this.commentDeleted.emit(commentId);
        this.snackBar.open('Комментарий удален', 'Закрыть', {
          duration: 3000,
        });
        this.loadComments();
        this.setActionLoading(commentId, false);
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error deleting comment:', error);
        this.snackBar.open('Ошибка при удалении комментария', 'Закрыть', {
          duration: 3000,
        });
        this.setActionLoading(commentId, false);
        this.cdr.markForCheck();
      },
    });
  }

  onPageChange(event: any): void {
    this.currentPageIndex.set(event.pageIndex);
    this.pageSizeValue.set(event.pageSize);
    this.loadComments();
  }

  clearFilters(): void {
    this.textControl.setValue('');
    this.groupIdControl.setValue('');
    this.keywordIdControl.setValue('');
    this.dateFromControl.setValue(null);
    this.dateToControl.setValue(null);
    this.isViewedControl.setValue(false);
    this.isArchivedControl.setValue(false);
    this.orderByControl.setValue('published_at');
    this.orderDirControl.setValue('desc');
  }
}
