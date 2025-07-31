import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormControl } from '@angular/forms';
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
import { Subject, takeUntil, debounceTime, distinctUntilChanged } from 'rxjs';

import {
  KeywordsService,
  KeywordsSearchParams,
} from '../../core/services/keywords.service';
import { KeywordResponse } from '../../core/models';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-keywords',
  template: `
    <div class="keywords-container">
      <mat-card>
        <mat-card-header>
          <mat-card-title>Keywords Management</mat-card-title>
          <mat-card-subtitle
            >Manage and monitor keywords for comment analysis</mat-card-subtitle
          >
        </mat-card-header>

        <mat-card-content>
          <!-- Search and Filters -->
          <div class="filters-section">
            <mat-form-field appearance="outline" class="search-field">
              <mat-label>Search keywords</mat-label>
              <input
                matInput
                [formControl]="searchControl"
                placeholder="Enter keyword or description"
              />
              <mat-icon matSuffix>search</mat-icon>
            </mat-form-field>

            <mat-form-field appearance="outline" class="category-field">
              <mat-label>Category</mat-label>
              <mat-select [formControl]="categoryControl">
                <mat-option value="">All categories</mat-option>
                <mat-option value="spam">Spam</mat-option>
                <mat-option value="offensive">Offensive</mat-option>
                <mat-option value="commercial">Commercial</mat-option>
                <mat-option value="other">Other</mat-option>
              </mat-select>
            </mat-form-field>

            <mat-checkbox
              [formControl]="activeOnlyControl"
              class="active-filter"
            >
              Active keywords only
            </mat-checkbox>
          </div>

          <!-- Loading State -->
          <div *ngIf="loading" class="loading-section">
            <app-loading-spinner
              message="Loading keywords..."
            ></app-loading-spinner>
          </div>

          <!-- Keywords Table -->
          <div *ngIf="!loading && keywords.length > 0" class="table-section">
            <table mat-table [dataSource]="keywords" matSort>
              <!-- Word Column -->
              <ng-container matColumnDef="word">
                <th mat-header-cell *matHeaderCellDef mat-sort-header>
                  Keyword
                </th>
                <td mat-cell *matCellDef="let keyword">
                  <div class="keyword-info">
                    <div class="keyword-word">{{ keyword.word }}</div>
                    <div
                      class="keyword-description"
                      *ngIf="keyword.description"
                    >
                      {{ keyword.description }}
                    </div>
                  </div>
                </td>
              </ng-container>

              <!-- Category Column -->
              <ng-container matColumnDef="category">
                <th mat-header-cell *matHeaderCellDef mat-sort-header>
                  Category
                </th>
                <td mat-cell *matCellDef="let keyword">
                  <mat-chip
                    *ngIf="keyword.category"
                    [color]="getCategoryColor(keyword.category)"
                    selected
                  >
                    {{ keyword.category }}
                  </mat-chip>
                  <span *ngIf="!keyword.category">-</span>
                </td>
              </ng-container>

              <!-- Matches Column -->
              <ng-container matColumnDef="matches">
                <th mat-header-cell *matHeaderCellDef mat-sort-header>
                  Matches
                </th>
                <td mat-cell *matCellDef="let keyword">
                  {{ keyword.total_matches }}
                </td>
              </ng-container>

              <!-- Settings Column -->
              <ng-container matColumnDef="settings">
                <th mat-header-cell *matHeaderCellDef>Settings</th>
                <td mat-cell *matCellDef="let keyword">
                  <div class="settings-chips">
                    <mat-chip
                      *ngIf="keyword.is_case_sensitive"
                      size="small"
                      color="primary"
                    >
                      Case Sensitive
                    </mat-chip>
                    <mat-chip
                      *ngIf="keyword.is_whole_word"
                      size="small"
                      color="accent"
                    >
                      Whole Word
                    </mat-chip>
                  </div>
                </td>
              </ng-container>

              <!-- Status Column -->
              <ng-container matColumnDef="status">
                <th mat-header-cell *matHeaderCellDef>Status</th>
                <td mat-cell *matCellDef="let keyword">
                  <mat-chip
                    [color]="keyword.is_active ? 'accent' : 'warn'"
                    selected
                  >
                    {{ keyword.is_active ? 'Active' : 'Inactive' }}
                  </mat-chip>
                </td>
              </ng-container>

              <!-- Actions Column -->
              <ng-container matColumnDef="actions">
                <th mat-header-cell *matHeaderCellDef>Actions</th>
                <td mat-cell *matCellDef="let keyword">
                  <button mat-icon-button [matMenuTriggerFor]="menu">
                    <mat-icon>more_vert</mat-icon>
                  </button>
                  <mat-menu #menu="matMenu">
                    <button mat-menu-item (click)="editKeyword(keyword)">
                      <mat-icon>edit</mat-icon>
                      <span>Edit</span>
                    </button>
                    <button
                      mat-menu-item
                      (click)="
                        toggleKeywordActive(keyword.id, !keyword.is_active)
                      "
                    >
                      <mat-icon>{{
                        keyword.is_active ? 'pause' : 'play_arrow'
                      }}</mat-icon>
                      <span>{{
                        keyword.is_active ? 'Deactivate' : 'Activate'
                      }}</span>
                    </button>
                    <button
                      mat-menu-item
                      (click)="deleteKeyword(keyword.id)"
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
          <div *ngIf="!loading && keywords.length === 0" class="empty-state">
            <mat-icon>key</mat-icon>
            <h3>No keywords found</h3>
            <p>Try adjusting your search criteria or add a new keyword.</p>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [
    `
      .keywords-container {
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

      .category-field {
        min-width: 200px;
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

      .keyword-info {
        display: flex;
        flex-direction: column;
      }

      .keyword-word {
        font-weight: 500;
      }

      .keyword-description {
        font-size: 0.875rem;
        color: #666;
      }

      .settings-chips {
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

      .mat-column-actions {
        width: 80px;
      }

      .mat-column-status {
        width: 120px;
      }

      .mat-column-matches {
        width: 100px;
      }

      .mat-column-settings {
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
    LoadingSpinnerComponent,
  ],
})
export class KeywordsComponent implements OnInit, OnDestroy {
  keywords: KeywordResponse[] = [];
  loading = false;
  totalItems = 0;
  currentPage = 0;
  pageSize = 25;
  displayedColumns = [
    'word',
    'category',
    'matches',
    'settings',
    'status',
    'actions',
  ];

  searchControl = new FormControl('');
  categoryControl = new FormControl('');
  activeOnlyControl = new FormControl(false);

  private destroy$ = new Subject<void>();

  constructor(
    private keywordsService: KeywordsService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.setupSearchSubscription();
    this.loadKeywords();
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
        this.loadKeywords();
      });

    this.categoryControl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.currentPage = 0;
        this.loadKeywords();
      });

    this.activeOnlyControl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.currentPage = 0;
        this.loadKeywords();
      });
  }

  private loadKeywords(): void {
    this.loading = true;

    const params: KeywordsSearchParams = {
      page: this.currentPage + 1,
      size: this.pageSize,
      search: this.searchControl.value || undefined,
      category: this.categoryControl.value || undefined,
      is_active: this.activeOnlyControl.value || undefined,
    };

    this.keywordsService
      .getKeywords(params)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.keywords = response.items;
          this.totalItems = response.total;
          this.loading = false;
        },
        error: (error) => {
          console.error('Error loading keywords:', error);
          this.snackBar.open('Error loading keywords', 'Close', {
            duration: 3000,
          });
          this.loading = false;
        },
      });
  }

  onPageChange(event: PageEvent): void {
    this.currentPage = event.pageIndex;
    this.pageSize = event.pageSize;
    this.loadKeywords();
  }

  getCategoryColor(category: string): string {
    switch (category.toLowerCase()) {
      case 'spam':
        return 'warn';
      case 'offensive':
        return 'accent';
      case 'commercial':
        return 'primary';
      default:
        return 'primary';
    }
  }

  editKeyword(keyword: KeywordResponse): void {
    // TODO: Implement edit dialog
    console.log('Edit keyword:', keyword);
  }

  toggleKeywordActive(keywordId: number, isActive: boolean): void {
    this.keywordsService
      .toggleKeywordActive(keywordId, isActive)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.snackBar.open(
            `Keyword ${isActive ? 'activated' : 'deactivated'}`,
            'Close',
            { duration: 2000 }
          );
          this.loadKeywords();
        },
        error: (error) => {
          console.error('Error toggling keyword status:', error);
          this.snackBar.open('Error updating keyword status', 'Close', {
            duration: 3000,
          });
        },
      });
  }

  deleteKeyword(keywordId: number): void {
    if (confirm('Are you sure you want to delete this keyword?')) {
      this.keywordsService
        .deleteKeyword(keywordId)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: () => {
            this.snackBar.open('Keyword deleted', 'Close', { duration: 2000 });
            this.loadKeywords();
          },
          error: (error) => {
            console.error('Error deleting keyword:', error);
            this.snackBar.open('Error deleting keyword', 'Close', {
              duration: 3000,
            });
          },
        });
    }
  }
}
