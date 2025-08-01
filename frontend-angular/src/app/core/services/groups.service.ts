import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface VKGroupResponse {
  id: string;
  vkId: number;
  screenName: string;
  name: string;
  description: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  postCount: number;
}

export interface CreateVKGroupRequest {
  vkId: number;
  screenName: string;
  name: string;
  description?: string;
}

export interface UpdateVKGroupRequest {
  name?: string;
  description?: string;
  isActive?: boolean;
}

export interface GroupsResponse {
  groups: VKGroupResponse[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface GroupsQueryParams {
  page?: number;
  limit?: number;
  search?: string;
  isActive?: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class GroupsService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/groups`;

  /**
   * Get all groups with pagination and filtering
   */
  getGroups(params: GroupsQueryParams = {}): Observable<GroupsResponse> {
    let httpParams = new HttpParams();

    if (params.page !== undefined) {
      httpParams = httpParams.set('page', params.page.toString());
    }
    if (params.limit !== undefined) {
      httpParams = httpParams.set('limit', params.limit.toString());
    }
    if (params.search) {
      httpParams = httpParams.set('search', params.search);
    }
    if (params.isActive !== undefined) {
      httpParams = httpParams.set('isActive', params.isActive.toString());
    }

    return this.http.get<GroupsResponse>(this.apiUrl, { params: httpParams });
  }

  /**
   * Get group by ID
   */
  getGroup(id: string): Observable<VKGroupResponse> {
    return this.http.get<VKGroupResponse>(`${this.apiUrl}/${id}`);
  }

  /**
   * Get group by VK ID
   */
  getGroupByVkId(vkId: number): Observable<VKGroupResponse> {
    return this.http.get<VKGroupResponse>(`${this.apiUrl}/vk/${vkId}`);
  }

  /**
   * Get group by screen name
   */
  getGroupByScreenName(screenName: string): Observable<VKGroupResponse> {
    return this.http.get<VKGroupResponse>(
      `${this.apiUrl}/screen/${screenName}`
    );
  }

  /**
   * Create new group
   */
  createGroup(group: CreateVKGroupRequest): Observable<VKGroupResponse> {
    return this.http.post<VKGroupResponse>(this.apiUrl, group);
  }

  /**
   * Update group
   */
  updateGroup(
    id: string,
    updates: UpdateVKGroupRequest
  ): Observable<VKGroupResponse> {
    return this.http.patch<VKGroupResponse>(`${this.apiUrl}/${id}`, updates);
  }

  /**
   * Delete group
   */
  deleteGroup(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  /**
   * Toggle group active status
   */
  toggleGroupActive(
    id: string,
    isActive: boolean
  ): Observable<VKGroupResponse> {
    return this.updateGroup(id, { isActive });
  }

  /**
   * Bulk update group status
   */
  bulkUpdateStatus(
    ids: string[],
    isActive: boolean
  ): Observable<VKGroupResponse[]> {
    return this.http.patch<VKGroupResponse[]>(`${this.apiUrl}/bulk-status`, {
      ids,
      isActive,
    });
  }

  /**
   * Search groups
   */
  searchGroups(query: string, limit?: number): Observable<VKGroupResponse[]> {
    let params = new HttpParams().set('q', query);
    if (limit) {
      params = params.set('limit', limit.toString());
    }
    return this.http.get<VKGroupResponse[]>(`${this.apiUrl}/search`, {
      params,
    });
  }

  /**
   * Get groups by post count
   */
  getGroupsByPostCount(minPosts?: number): Observable<VKGroupResponse[]> {
    let params = new HttpParams();
    if (minPosts) {
      params = params.set('minPosts', minPosts.toString());
    }
    return this.http.get<VKGroupResponse[]>(`${this.apiUrl}/by-posts`, {
      params,
    });
  }

  /**
   * Get groups statistics
   */
  getGroupsStatistics(): Observable<any> {
    return this.http.get(`${this.apiUrl}/statistics`);
  }
}
