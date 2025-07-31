import { Injectable } from '@angular/core';
import { Observable, catchError, tap } from 'rxjs';
import { ApiService, ApiError } from './api.service';
import { ErrorHandlerService } from './error-handler.service';
import { LoadingService } from './loading.service';
import {
  VKCommentResponse,
  CommentWithKeywords,
  CommentUpdateRequest,
  CommentSearchParams,
  PaginatedResponse,
} from '../models';

@Injectable({
  providedIn: 'root',
})
export class CommentsService {
  constructor(
    private apiService: ApiService,
    private errorHandler: ErrorHandlerService,
    private loadingService: LoadingService
  ) {}

  getComments(
    params: CommentSearchParams = {}
  ): Observable<PaginatedResponse<VKCommentResponse>> {
    const queryParams = new URLSearchParams();

    if (params.text) {
      queryParams.append('text', params.text);
    }
    if (params.group_id) {
      queryParams.append('group_id', params.group_id.toString());
    }
    if (params.keyword_id) {
      queryParams.append('keyword_id', params.keyword_id.toString());
    }
    if (params.author_id) {
      queryParams.append('author_id', params.author_id.toString());
    }
    if (params.author_screen_name && params.author_screen_name.length > 0) {
      params.author_screen_name.forEach((name) => {
        queryParams.append('author_screen_name', name);
      });
    }
    if (params.date_from) {
      queryParams.append('date_from', params.date_from);
    }
    if (params.date_to) {
      queryParams.append('date_to', params.date_to);
    }
    if (params.is_viewed !== undefined) {
      queryParams.append('is_viewed', params.is_viewed.toString());
    }
    if (params.is_archived !== undefined) {
      queryParams.append('is_archived', params.is_archived.toString());
    }
    if (params.order_by) {
      queryParams.append('order_by', params.order_by);
    }
    if (params.order_dir) {
      queryParams.append('order_dir', params.order_dir);
    }

    const queryString = queryParams.toString();
    const endpoint = queryString ? `/comments?${queryString}` : '/comments';

    this.loadingService.show('Loading comments...');

    return this.apiService
      .get<PaginatedResponse<VKCommentResponse>>(endpoint)
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

  getComment(id: number): Observable<CommentWithKeywords> {
    this.loadingService.show('Loading comment details...');

    return this.apiService.get<CommentWithKeywords>(`/comments/${id}`).pipe(
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

  updateComment(
    id: number,
    update: CommentUpdateRequest
  ): Observable<VKCommentResponse> {
    this.loadingService.show('Updating comment...');

    return this.apiService
      .patch<VKCommentResponse>(`/comments/${id}`, update)
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            'Comment updated successfully'
          );
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  deleteComment(id: number): Observable<void> {
    this.loadingService.show('Deleting comment...');

    return this.apiService.delete<void>(`/comments/${id}`).pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification(
          'Comment deleted successfully'
        );
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  markAsViewed(id: number): Observable<VKCommentResponse> {
    this.loadingService.show('Marking comment as viewed...');

    return this.updateComment(id, { is_viewed: true }).pipe(
      tap(() => {
        this.errorHandler.showSuccessNotification('Comment marked as viewed');
      }),
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  markAsArchived(id: number): Observable<VKCommentResponse> {
    this.loadingService.show('Archiving comment...');

    return this.updateComment(id, { is_archived: true }).pipe(
      tap(() => {
        this.errorHandler.showSuccessNotification(
          'Comment archived successfully'
        );
      }),
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  bulkUpdate(
    ids: number[],
    update: CommentUpdateRequest
  ): Observable<VKCommentResponse[]> {
    this.loadingService.show('Updating selected comments...');

    return this.apiService
      .patch<VKCommentResponse[]>(`/comments/bulk`, {
        ids,
        ...update,
      })
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            `${ids.length} comments updated successfully`
          );
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  bulkDeleteComments(commentIds: number[]): Observable<void> {
    this.loadingService.show('Deleting selected comments...');

    return this.apiService
      .post<void>('/comments/bulk-delete', { comment_ids: commentIds })
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            `${commentIds.length} comments deleted successfully`
          );
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  bulkMarkAsViewed(commentIds: number[]): Observable<void> {
    this.loadingService.show('Marking comments as viewed...');

    return this.apiService
      .post<void>('/comments/bulk-mark-viewed', { comment_ids: commentIds })
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            `${commentIds.length} comments marked as viewed`
          );
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  bulkArchiveComments(commentIds: number[]): Observable<void> {
    this.loadingService.show('Archiving selected comments...');

    return this.apiService
      .post<void>('/comments/bulk-archive', { comment_ids: commentIds })
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            `${commentIds.length} comments archived successfully`
          );
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  exportComments(params: CommentSearchParams = {}): Observable<Blob> {
    this.loadingService.show('Exporting comments...');

    const queryParams = new URLSearchParams();

    // Add all search parameters for export
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach((v) => queryParams.append(key, v));
        } else {
          queryParams.append(key, value.toString());
        }
      }
    });

    const queryString = queryParams.toString();
    const endpoint = queryString
      ? `/comments/export?${queryString}`
      : '/comments/export';

    return this.apiService.download(endpoint).pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification(
          'Comments exported successfully'
        );
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  // Get comment statistics
  getCommentStats(): Observable<{
    total: number;
    viewed: number;
    archived: number;
    today: number;
  }> {
    this.loadingService.show('Loading comment statistics...');

    return this.apiService
      .get<{
        total: number;
        viewed: number;
        archived: number;
        today: number;
      }>('/comments/stats')
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
}
