import {
  Component,
  computed,
  signal,
  input,
  output,
  inject,
  OnInit,
  OnDestroy,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  ReactiveFormsModule,
  FormControl,
  FormBuilder,
  FormGroup,
} from '@angular/forms';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
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
import { Subject, debounceTime, distinctUntilChanged, takeUntil } from 'rxjs';
import { ChangeDetectionStrategy } from '@angular/core';

// Interfaces
interface Keyword {
  id: string;
  word: string;
  description?: string;
  category?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

interface KeywordsResponse {
  keywords: Keyword[];
  total: number;
}

@Component({
  selector: 'app-keywords',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
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
  ],
  templateUrl: './keywords.component.html',
  styleUrls: ['./keywords.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class KeywordsComponent implements OnInit, OnDestroy {
  // Inputs
  initialFilters = input<Partial<any>>({});

  // Outputs
  keywordDeleted = output<string>();
  keywordToggled = output<{ id: string; isActive: boolean }>();

  // Dependencies
  private readonly http = inject(HttpClient);
  private readonly snackBar = inject(MatSnackBar);
  private readonly destroy$ = new Subject<void>();

  // API endpoints
  private readonly apiUrl = environment.apiUrl;

  // Signals
  keywords = signal<Keyword[]>([]);
  loading = signal(false);
  error = signal('');
  currentPage = signal(0);
  pageSize = signal(10);
  totalItems = signal(0);
  actionLoadingIds = signal<Set<string>>(new Set());

  // Form controls
  searchControl = new FormControl('');
  categoryControl = new FormControl('all');
  activeOnlyControl = new FormControl(false);

  // Computed values
  filteredKeywords = computed(() => {
    const filters = {
      search: this.searchControl.value || '',
      category: this.categoryControl.value || '',
      activeOnly: this.activeOnlyControl.value || false,
    };

    return this.keywords().filter((keyword) => {
      const matchesSearch =
        !filters.search ||
        keyword.word.toLowerCase().includes(filters.search.toLowerCase());

      const matchesCategory =
        !filters.category ||
        filters.category === 'all' ||
        keyword.category === filters.category;

      const matchesActive = !filters.activeOnly || keyword.isActive;

      return matchesSearch && matchesCategory && matchesActive;
    });
  });

  // Table columns
  displayedColumns = computed(() => [
    'word',
    'category',
    'isActive',
    'createdAt',
    'actions',
  ]);

  ngOnInit(): void {
    this.setupFormListeners();
    this.loadKeywords();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private setupFormListeners(): void {
    // Debounced search
    this.searchControl.valueChanges
      .pipe(debounceTime(300), distinctUntilChanged(), takeUntil(this.destroy$))
      .subscribe(() => {
        this.currentPage.set(0);
        this.loadKeywords();
      });

    // Category filter
    this.categoryControl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.currentPage.set(0);
        this.loadKeywords();
      });

    // Active only filter
    this.activeOnlyControl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.currentPage.set(0);
        this.loadKeywords();
      });
  }

  private loadKeywords(): void {
    this.loading.set(true);
    this.error.set('');

    const params = new HttpParams()
      .set('page', (this.currentPage() + 1).toString()) // API использует 1-based pagination
      .set('limit', this.pageSize().toString());

    if (this.searchControl.value) {
      params.set('search', this.searchControl.value);
    }

    if (this.categoryControl.value && this.categoryControl.value !== 'all') {
      params.set('category', this.categoryControl.value);
    }

    if (this.activeOnlyControl.value) {
      params.set('active_only', 'true');
    }

    this.http
      .get<KeywordsResponse>(`${this.apiUrl}/keywords`, { params })
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.keywords.set(response.keywords);
          this.totalItems.set(response.total);
          this.loading.set(false);
        },
        error: (error) => {
          console.error('Error loading keywords:', error);
          this.error.set('Ошибка загрузки ключевых слов');
          this.loading.set(false);
        },
      });
  }

  onSortChange(sort: Sort): void {
    // Implement sorting logic if needed
    console.log('Sort changed:', sort);
  }

  getCategoryLabel(category: string): string {
    const categoryLabels: Record<string, string> = {
      spam: 'Спам',
      offensive: 'Оскорбления',
      commercial: 'Коммерческие',
      other: 'Другие',
    };
    return categoryLabels[category] || category;
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

  deleteKeyword(id: string): void {
    if (confirm('Вы уверены, что хотите удалить это ключевое слово?')) {
      this.setActionLoading(id, true);
      this.http
        .delete(`${this.apiUrl}/keywords/${id}`)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: () => {
            this.snackBar.open('Ключевое слово удалено', 'Закрыть', {
              duration: 3000,
            });
            this.loadKeywords();
            this.setActionLoading(id, false);
          },
          error: (error) => {
            console.error('Error deleting keyword:', error);
            this.snackBar.open('Ошибка удаления ключевого слова', 'Закрыть', {
              duration: 5000,
            });
            this.setActionLoading(id, false);
          },
        });
    }
  }

  toggleKeywordActive(id: string, isActive: boolean): void {
    this.setActionLoading(id, true);
    this.http
      .patch<Keyword>(`${this.apiUrl}/keywords/${id}/toggle`, {
        isActive,
      })
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.snackBar.open('Статус ключевого слова изменен', 'Закрыть', {
            duration: 3000,
          });
          this.loadKeywords();
          this.setActionLoading(id, false);
        },
        error: (error) => {
          console.error('Error toggling keyword status:', error);
          this.snackBar.open('Ошибка изменения статуса', 'Закрыть', {
            duration: 5000,
          });
          this.setActionLoading(id, false);
        },
      });
  }

  onPageChange(pageIndex: number): void {
    this.currentPage.set(pageIndex);
    this.loadKeywords();
  }

  onPageSizeChange(pageSize: number): void {
    this.pageSize.set(pageSize);
    this.currentPage.set(0);
    this.loadKeywords();
  }

  clearFilters(): void {
    this.searchControl.setValue('');
    this.categoryControl.setValue('all');
    this.activeOnlyControl.setValue(false);
    this.currentPage.set(0);
    this.loadKeywords();
  }
}
