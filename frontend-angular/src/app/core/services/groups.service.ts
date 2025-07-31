import { Injectable } from '@angular/core';
import { Observable, catchError, tap } from 'rxjs';
import { ApiService, ApiError } from './api.service';
import { ErrorHandlerService } from './error-handler.service';
import { LoadingService } from './loading.service';
import { CacheService } from './cache.service';
import {
  VKGroupResponse,
  VKGroupCreate,
  VKGroupUpdate,
  VKGroupStats,
  PaginatedResponse,
} from '../models';

export interface GroupsSearchParams {
  active_only?: boolean;
  search?: string;
  page?: number;
  size?: number;
}

@Injectable({
  providedIn: 'root',
})
export class GroupsService {
  constructor(
    private apiService: ApiService,
    private errorHandler: ErrorHandlerService,
    private loadingService: LoadingService,
    private cacheService: CacheService
  ) {}

  getGroups(
    params: GroupsSearchParams = {}
  ): Observable<PaginatedResponse<VKGroupResponse>> {
    const queryParams = new URLSearchParams();

    if (params.active_only !== undefined) {
      queryParams.append('active_only', params.active_only.toString());
    }
    if (params.search) {
      queryParams.append('search', params.search);
    }
    if (params.page) {
      queryParams.append('page', params.page.toString());
    }
    if (params.size) {
      queryParams.append('size', params.size.toString());
    }

    const queryString = queryParams.toString();
    const endpoint = queryString ? `/groups?${queryString}` : '/groups';
    const cacheKey = `groups_${endpoint}`;

    this.loadingService.show('Loading groups...');

    return this.cacheService
      .getOrSet(
        cacheKey,
        () => this.apiService.get<PaginatedResponse<VKGroupResponse>>(endpoint),
        2 * 60 * 1000 // 2 minutes cache
      )
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

  getGroup(id: number): Observable<VKGroupResponse> {
    this.loadingService.show('Loading group details...');

    return this.apiService.get<VKGroupResponse>(`/groups/${id}`).pipe(
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

  createGroup(group: VKGroupCreate): Observable<VKGroupResponse> {
    this.loadingService.show('Creating group...');

    return this.apiService.post<VKGroupResponse>('/groups', group).pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification('Group created successfully');
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  updateGroup(id: number, group: VKGroupUpdate): Observable<VKGroupResponse> {
    this.loadingService.show('Updating group...');

    return this.apiService.put<VKGroupResponse>(`/groups/${id}`, group).pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification('Group updated successfully');
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  deleteGroup(id: number): Observable<void> {
    this.loadingService.show('Deleting group...');

    return this.apiService.delete<void>(`/groups/${id}`).pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification('Group deleted successfully');
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  getGroupStats(id: number): Observable<VKGroupStats> {
    this.loadingService.show('Loading group statistics...');

    return this.apiService.get<VKGroupStats>(`/groups/${id}/stats`).pipe(
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

  refreshGroupInfo(id: number): Observable<VKGroupResponse> {
    this.loadingService.show('Refreshing group information...');

    return this.apiService
      .post<VKGroupResponse>(`/groups/${id}/refresh`, {})
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            'Group information refreshed successfully'
          );
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  toggleGroupActive(
    id: number,
    isActive: boolean
  ): Observable<VKGroupResponse> {
    const action = isActive ? 'activating' : 'deactivating';
    this.loadingService.show(`${action} group...`);

    return this.apiService
      .patch<VKGroupResponse>(`/groups/${id}`, {
        is_active: isActive,
      })
      .pipe(
        tap(() => {
          this.loadingService.hide();
          const message = isActive
            ? 'Group activated successfully'
            : 'Group deactivated successfully';
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
  bulkDeleteGroups(groupIds: number[]): Observable<void> {
    this.loadingService.show('Deleting selected groups...');

    return this.apiService
      .post<void>('/groups/bulk-delete', { group_ids: groupIds })
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            `${groupIds.length} groups deleted successfully`
          );
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  bulkActivateGroups(groupIds: number[]): Observable<void> {
    this.loadingService.show('Activating selected groups...');

    return this.apiService
      .post<void>('/groups/bulk-activate', { group_ids: groupIds })
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            `${groupIds.length} groups activated successfully`
          );
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  bulkDeactivateGroups(groupIds: number[]): Observable<void> {
    this.loadingService.show('Deactivating selected groups...');

    return this.apiService
      .post<void>('/groups/bulk-deactivate', { group_ids: groupIds })
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            `${groupIds.length} groups deactivated successfully`
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
  exportGroups(params: GroupsSearchParams = {}): Observable<Blob> {
    this.loadingService.show('Exporting groups...');

    const queryParams = new URLSearchParams();
    if (params.active_only !== undefined) {
      queryParams.append('active_only', params.active_only.toString());
    }
    if (params.search) {
      queryParams.append('search', params.search);
    }

    const queryString = queryParams.toString();
    const endpoint = queryString
      ? `/groups/export?${queryString}`
      : '/groups/export';

    return this.apiService.download(endpoint).pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification(
          'Groups exported successfully'
        );
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }
}
