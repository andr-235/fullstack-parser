import { Injectable } from '@angular/core';
import { Observable, catchError, tap } from 'rxjs';
import { ApiService, ApiError } from './api.service';
import { ErrorHandlerService } from './error-handler.service';
import { LoadingService } from './loading.service';

export interface ParserStatus {
  is_running: boolean;
  last_run?: string;
  next_run?: string;
  total_groups: number;
  active_groups: number;
  total_comments_parsed: number;
  comments_with_keywords: number;
  errors_count: number;
  current_progress?: {
    group_id: number;
    group_name: string;
    progress_percentage: number;
    comments_parsed: number;
  };
}

export interface ParserConfig {
  auto_parse_enabled: boolean;
  parse_interval_minutes: number;
  max_posts_per_group: number;
  max_comments_per_post: number;
  parse_delay_seconds: number;
}

export interface ParseRequest {
  group_ids?: number[];
  force_parse?: boolean;
  max_posts?: number;
}

export interface ParserLog {
  id: number;
  timestamp: string;
  level: 'INFO' | 'WARNING' | 'ERROR';
  message: string;
  group_id?: number;
  group_name?: string;
  details?: any;
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

  getParserStatus(): Observable<ParserStatus> {
    this.loadingService.show('Loading parser status...');

    return this.apiService.get<ParserStatus>('/parser/status').pipe(
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

  getParserConfig(): Observable<ParserConfig> {
    this.loadingService.show('Loading parser configuration...');

    return this.apiService.get<ParserConfig>('/parser/config').pipe(
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

  updateParserConfig(config: Partial<ParserConfig>): Observable<ParserConfig> {
    this.loadingService.show('Updating parser configuration...');

    return this.apiService.put<ParserConfig>('/parser/config', config).pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification(
          'Parser configuration updated successfully'
        );
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  startParsing(request: ParseRequest = {}): Observable<{ message: string }> {
    this.loadingService.show('Starting parser...');

    return this.apiService
      .post<{ message: string }>('/parser/start', request)
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            'Parser started successfully'
          );
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  stopParsing(): Observable<{ message: string }> {
    this.loadingService.show('Stopping parser...');

    return this.apiService.post<{ message: string }>('/parser/stop', {}).pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification(
          'Parser stopped successfully'
        );
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  parseGroup(
    groupId: number,
    request: ParseRequest = {}
  ): Observable<{ message: string }> {
    this.loadingService.show('Starting group parsing...');

    return this.apiService
      .post<{ message: string }>(`/parser/groups/${groupId}/parse`, request)
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            'Group parsing started successfully'
          );
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  parseAllGroups(request: ParseRequest = {}): Observable<{ message: string }> {
    this.loadingService.show('Starting parsing for all groups...');

    return this.apiService
      .post<{ message: string }>('/parser/groups/parse-all', request)
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification(
            'Parsing started for all groups'
          );
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  getParserLogs(limit: number = 100): Observable<ParserLog[]> {
    this.loadingService.show('Loading parser logs...');

    return this.apiService.get<ParserLog[]>(`/parser/logs?limit=${limit}`).pipe(
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

  clearParserLogs(): Observable<{ message: string }> {
    this.loadingService.show('Clearing parser logs...');

    return this.apiService.delete<{ message: string }>('/parser/logs').pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification(
          'Parser logs cleared successfully'
        );
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  // Additional parser methods
  pauseParsing(): Observable<{ message: string }> {
    this.loadingService.show('Pausing parser...');

    return this.apiService.post<{ message: string }>('/parser/pause', {}).pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification('Parser paused successfully');
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  resumeParsing(): Observable<{ message: string }> {
    this.loadingService.show('Resuming parser...');

    return this.apiService.post<{ message: string }>('/parser/resume', {}).pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification(
          'Parser resumed successfully'
        );
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  getParserStatistics(): Observable<{
    total_runs: number;
    successful_runs: number;
    failed_runs: number;
    total_comments_parsed: number;
    average_comments_per_run: number;
    last_successful_run?: string;
  }> {
    this.loadingService.show('Loading parser statistics...');

    return this.apiService
      .get<{
        total_runs: number;
        successful_runs: number;
        failed_runs: number;
        total_comments_parsed: number;
        average_comments_per_run: number;
        last_successful_run?: string;
      }>('/parser/statistics')
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

  exportParserLogs(): Observable<Blob> {
    this.loadingService.show('Exporting parser logs...');

    return this.apiService.download('/parser/logs/export').pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification(
          'Parser logs exported successfully'
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
