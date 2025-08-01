import { Injectable } from '@angular/core';
import { Observable, catchError, tap, map } from 'rxjs';
import { ApiService, ApiError } from './api.service';
import { ErrorHandlerService } from './error-handler.service';
import { LoadingService } from './loading.service';
import { PaginatedResponse, VKGroupResponse } from '../models/vk-group.model';

export interface VKGroup {
  id: string;
  vkId: number;
  screenName: string;
  name: string;
  description?: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface VKPost {
  id: string;
  vkId: number;
  text: string;
  createdAt: Date;
  updatedAt: Date;
  groupId: string;
}

export interface VKComment {
  id: string;
  vkId: number;
  text: string;
  createdAt: Date;
  updatedAt: Date;
  postId: string;
}

export interface ParsingStats {
  totalGroups: number;
  totalPosts: number;
  totalComments: number;
  totalKeywords: number;
  totalMatches: number;
}

export interface GroupStats {
  group: VKGroup;
  postsCount: number;
  commentsCount: number;
  matchesCount: number;
}

export interface FullParseResult {
  group: VKGroup;
  postsParsed: number;
  commentsParsed: number;
  keywordsMatched: number;
}

export interface VKUser {
  id: number;
  first_name: string;
  last_name: string;
  screen_name?: string;
  photo_100?: string;
  deactivated?: string;
}

export interface VKGroupInfo {
  id: number;
  name: string;
  screen_name: string;
  photo_100?: string;
  type: string;
  is_closed: number;
  is_admin: number;
  is_member: number;
  is_advertiser: number;
}

export interface VKWallResponse {
  count: number;
  items: any[];
}

export interface TokenCheckResult {
  valid: boolean;
}

// Task management interfaces
export interface ParseTaskCreate {
  groupIds: string[];
  postsLimit?: number;
  commentsLimit?: number;
}

export interface ParseTaskResponse {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  totalGroups: number;
  processedGroups: number;
  currentGroup?: string;
  progress: number;
  createdAt: Date;
  completedAt?: Date;
  error?: string;
  results?: any;
}

export interface ParseTaskStatus {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  totalGroups: number;
  processedGroups: number;
  currentGroup?: string;
  progress: number;
  createdAt: Date;
  completedAt?: Date;
  error?: string;
  results?: any;
}

@Injectable({
  providedIn: 'root',
})
export class ParserService {
  constructor(
    private apiService: ApiService,
    private errorHandler: ErrorHandlerService,
    private loadingService: LoadingService
  ) {}

  // Task management methods
  createParseTask(taskData: ParseTaskCreate): Observable<ParseTaskResponse> {
    return this.apiService
      .post<ParseTaskResponse>('/parser/tasks', taskData)
      .pipe(
        tap(() => this.loadingService.hide()),
        catchError((error: ApiError) => {
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  getParseTaskStatus(taskId: string): Observable<ParseTaskStatus> {
    return this.apiService.get<ParseTaskStatus>(`/parser/tasks/${taskId}`).pipe(
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  getAllParseTasks(): Observable<ParseTaskResponse[]> {
    return this.apiService.get<ParseTaskResponse[]>('/parser/tasks').pipe(
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  cancelParseTask(taskId: string): Observable<{ message: string }> {
    return this.apiService
      .delete<{ message: string }>(`/parser/tasks/${taskId}`)
      .pipe(
        catchError((error: ApiError) => {
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  // Data retrieval methods (no parsing logic)
  getParsingStats(): Observable<ParsingStats> {
    return this.apiService.get<ParsingStats>('/parser/stats').pipe(
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  getGroupStats(groupId: string): Observable<GroupStats> {
    return this.apiService
      .get<GroupStats>(`/parser/groups/${groupId}/stats`)
      .pipe(
        catchError((error: ApiError) => {
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  getVkUser(userId: string): Observable<VKUser> {
    return this.apiService.get<VKUser>(`/parser/vk/user/${userId}`).pipe(
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  getVkGroup(groupId: string): Observable<VKGroupInfo> {
    return this.apiService.get<VKGroupInfo>(`/parser/vk/group/${groupId}`).pipe(
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  getVkWallPosts(
    ownerId: number,
    count: number = 100,
    offset: number = 0
  ): Observable<VKWallResponse> {
    return this.apiService
      .get<VKWallResponse>(
        `/parser/vk/wall/${ownerId}?count=${count}&offset=${offset}`
      )
      .pipe(
        catchError((error: ApiError) => {
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  searchVkPosts(
    query: string,
    ownerId?: number,
    count: number = 100
  ): Observable<VKWallResponse> {
    let url = `/parser/vk/search?query=${encodeURIComponent(
      query
    )}&count=${count}`;
    if (ownerId) {
      url += `&ownerId=${ownerId}`;
    }
    return this.apiService.get<VKWallResponse>(url).pipe(
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  checkVkToken(): Observable<TokenCheckResult> {
    return this.apiService.get<TokenCheckResult>('/parser/vk/token/check').pipe(
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  // Group management methods
  getGroups(): Observable<VKGroup[]> {
    return this.apiService.get<VKGroup[]>('/groups').pipe(
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  getAllGroups(): Observable<VKGroup[]> {
    return this.apiService.get<VKGroup[]>('/groups/all').pipe(
      catchError((error: ApiError) => {
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }
}
