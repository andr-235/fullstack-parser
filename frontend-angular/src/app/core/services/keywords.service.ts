import { Injectable } from '@angular/core';
import { Observable, catchError, tap } from 'rxjs';
import { ApiService, ApiError } from './api.service';
import { ErrorHandlerService } from './error-handler.service';
import { LoadingService } from './loading.service';
import {
  KeywordResponse,
  KeywordCreate,
  KeywordUpdate,
  KeywordStats,
  PaginatedResponse,
} from '../models';

export interface KeywordsSearchParams {
  search?: string;
  category?: string;
  is_active?: boolean;
  page?: number;
  size?: number;
}

@Injectable({
  providedIn: 'root',
})
export class KeywordsService {
  constructor(
    private apiService: ApiService,
    private errorHandler: ErrorHandlerService,
    private loadingService: LoadingService
  ) {}

  getKeywords(
    params: KeywordsSearchParams = {}
  ): Observable<PaginatedResponse<KeywordResponse>> {
    const queryParams = new URLSearchParams();

    if (params.search) {
      queryParams.append('search', params.search);
    }
    if (params.category) {
      queryParams.append('category', params.category);
    }
    if (params.is_active !== undefined) {
      queryParams.append('is_active', params.is_active.toString());
    }
    if (params.page) {
      queryParams.append('page', params.page.toString());
    }
    if (params.size) {
      queryParams.append('size', params.size.toString());
    }

    const queryString = queryParams.toString();
    const endpoint = queryString ? `/keywords?${queryString}` : '/keywords';

    this.loadingService.show('Loading keywords...');

    return this.apiService
      .get<PaginatedResponse<KeywordResponse>>(endpoint)
      .pipe(
        tap(() => {
          this.loadingService.hide();
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  getKeyword(id: number): Observable<KeywordResponse> {
    this.loadingService.show('Loading keyword details...');

    return this.apiService.get<KeywordResponse>(`/keywords/${id}`).pipe(
      tap(() => {
        this.loadingService.hide();
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  createKeyword(keyword: KeywordCreate): Observable<KeywordResponse> {
    this.loadingService.show('Creating keyword...');

    return this.apiService.post<KeywordResponse>('/keywords', keyword).pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification(
          'Keyword created successfully'
        );
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  updateKeyword(
    id: number,
    keyword: KeywordUpdate
  ): Observable<KeywordResponse> {
    this.loadingService.show('Updating keyword...');

    return this.apiService
      .put<KeywordResponse>(`/keywords/${id}`, keyword)
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            'Keyword updated successfully'
          );
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  deleteKeyword(id: number): Observable<void> {
    this.loadingService.show('Deleting keyword...');

    return this.apiService.delete<void>(`/keywords/${id}`).pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification(
          'Keyword deleted successfully'
        );
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  getKeywordStats(id: number): Observable<KeywordStats> {
    this.loadingService.show('Loading keyword statistics...');

    return this.apiService.get<KeywordStats>(`/keywords/${id}/stats`).pipe(
      tap(() => {
        this.loadingService.hide();
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  toggleKeywordActive(
    id: number,
    isActive: boolean
  ): Observable<KeywordResponse> {
    const action = isActive ? 'activating' : 'deactivating';
    this.loadingService.show(`${action} keyword...`);

    return this.apiService
      .patch<KeywordResponse>(`/keywords/${id}`, {
        is_active: isActive,
      })
      .pipe(
        tap(() => {
          this.loadingService.hide();
          const message = isActive
            ? 'Keyword activated successfully'
            : 'Keyword deactivated successfully';
          this.errorHandler.showSuccessNotification(message);
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  // Bulk operations
  bulkDeleteKeywords(keywordIds: number[]): Observable<void> {
    this.loadingService.show('Deleting selected keywords...');

    return this.apiService
      .post<void>('/keywords/bulk-delete', { keyword_ids: keywordIds })
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            `${keywordIds.length} keywords deleted successfully`
          );
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  bulkActivateKeywords(keywordIds: number[]): Observable<void> {
    this.loadingService.show('Activating selected keywords...');

    return this.apiService
      .post<void>('/keywords/bulk-activate', { keyword_ids: keywordIds })
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            `${keywordIds.length} keywords activated successfully`
          );
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  bulkDeactivateKeywords(keywordIds: number[]): Observable<void> {
    this.loadingService.show('Deactivating selected keywords...');

    return this.apiService
      .post<void>('/keywords/bulk-deactivate', { keyword_ids: keywordIds })
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            `${keywordIds.length} keywords deactivated successfully`
          );
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  // Export functionality
  exportKeywords(params: KeywordsSearchParams = {}): Observable<Blob> {
    this.loadingService.show('Exporting keywords...');

    const queryParams = new URLSearchParams();
    if (params.search) {
      queryParams.append('search', params.search);
    }
    if (params.category) {
      queryParams.append('category', params.category);
    }
    if (params.is_active !== undefined) {
      queryParams.append('is_active', params.is_active.toString());
    }

    const queryString = queryParams.toString();
    const endpoint = queryString
      ? `/keywords/export?${queryString}`
      : '/keywords/export';

    return this.apiService.download(endpoint).pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification(
          'Keywords exported successfully'
        );
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  // Get keyword categories
  getKeywordCategories(): Observable<string[]> {
    this.loadingService.show('Loading keyword categories...');

    return this.apiService.get<string[]>('/keywords/categories').pipe(
      tap(() => {
        this.loadingService.hide();
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }
}
