import { Injectable } from '@angular/core';
import { Observable, catchError, tap } from 'rxjs';
import { ApiService, ApiError } from './api.service';
import { ErrorHandlerService } from './error-handler.service';
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
    private errorHandler: ErrorHandlerService
  ) {}

  getKeywords(
    params: KeywordsSearchParams = {}
  ): Observable<PaginatedResponse<KeywordResponse>> {
    const queryParams: any = {};

    if (params.search) {
      queryParams.search = params.search;
    }
    if (params.category) {
      queryParams.category = params.category;
    }
    if (params.is_active !== undefined) {
      queryParams.isActive = params.is_active;
    }
    if (params.page) {
      queryParams.page = params.page.toString();
    }
    if (params.size) {
      queryParams.limit = params.size.toString();
    }

    return this.apiService
      .get<PaginatedResponse<KeywordResponse>>('/keywords', queryParams)
      .pipe(
        tap((response) => {
          // Преобразуем ответ backend в формат frontend
          if (response.keywords) {
            response.items = response.keywords;
          }
        }),
        catchError((error: ApiError) => {
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  getKeyword(id: number): Observable<KeywordResponse> {
    return this.apiService.get<KeywordResponse>(`/keywords/${id}`).pipe(
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  createKeyword(keyword: KeywordCreate): Observable<KeywordResponse> {
    // Преобразуем данные в формат backend
    const createData = {
      word: keyword.word,
      isActive: keyword.is_active,
    };

    return this.apiService.post<KeywordResponse>('/keywords', createData).pipe(
      tap(() => {
        this.errorHandler.showSuccessNotification(
          'Keyword created successfully'
        );
      }),
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  updateKeyword(
    id: number,
    keyword: KeywordUpdate
  ): Observable<KeywordResponse> {
    return this.apiService
      .put<KeywordResponse>(`/keywords/${id}`, keyword)
      .pipe(
        tap(() => {
          this.errorHandler.showSuccessNotification(
            'Keyword updated successfully'
          );
        }),
        catchError((error: ApiError) => {
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  deleteKeyword(id: number): Observable<void> {
    return this.apiService.delete<void>(`/keywords/${id}`).pipe(
      tap(() => {
        this.errorHandler.showSuccessNotification(
          'Keyword deleted successfully'
        );
      }),
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  getKeywordStats(id: number): Observable<KeywordStats> {
    return this.apiService.get<KeywordStats>(`/keywords/${id}/stats`).pipe(
      catchError((error: ApiError) => {
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

    return this.apiService
      .patch<KeywordResponse>(`/keywords/${id}`, {
        is_active: isActive,
      })
      .pipe(
        tap(() => {
          const message = isActive
            ? 'Keyword activated successfully'
            : 'Keyword deactivated successfully';
          this.errorHandler.showSuccessNotification(message);
        }),
        catchError((error: ApiError) => {
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  // Bulk operations
  bulkDeleteKeywords(keywordIds: number[]): Observable<void> {
    return this.apiService
      .post<void>('/keywords/bulk-delete', { keyword_ids: keywordIds })
      .pipe(
        tap(() => {
          this.errorHandler.showSuccessNotification(
            `${keywordIds.length} keywords deleted successfully`
          );
        }),
        catchError((error: ApiError) => {
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  bulkActivateKeywords(keywordIds: number[]): Observable<void> {
    return this.apiService
      .post<void>('/keywords/bulk-activate', { keyword_ids: keywordIds })
      .pipe(
        tap(() => {
          this.errorHandler.showSuccessNotification(
            `${keywordIds.length} keywords activated successfully`
          );
        }),
        catchError((error: ApiError) => {
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  bulkDeactivateKeywords(keywordIds: number[]): Observable<void> {
    return this.apiService
      .post<void>('/keywords/bulk-deactivate', { keyword_ids: keywordIds })
      .pipe(
        tap(() => {
          this.errorHandler.showSuccessNotification(
            `${keywordIds.length} keywords deactivated successfully`
          );
        }),
        catchError((error: ApiError) => {
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  // Export functionality
  exportKeywords(params: KeywordsSearchParams = {}): Observable<Blob> {
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
        this.errorHandler.showSuccessNotification(
          'Keywords exported successfully'
        );
      }),
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  // Get keyword categories
  getKeywordCategories(): Observable<string[]> {
    return this.apiService.get<string[]>('/keywords/categories').pipe(
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }
}
