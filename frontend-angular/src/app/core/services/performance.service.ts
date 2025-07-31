import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, interval } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

export interface PerformanceMetrics {
  memoryUsage: number;
  cpuUsage: number;
  responseTime: number;
  cacheHitRatio: number;
  bundleSize: number;
  loadTime: number;
}

export interface PerformanceAlert {
  type: 'warning' | 'error';
  message: string;
  timestamp: Date;
  metric: keyof PerformanceMetrics;
  value: number;
  threshold: number;
}

@Injectable({
  providedIn: 'root',
})
export class PerformanceService {
  private metricsSubject = new BehaviorSubject<PerformanceMetrics>({
    memoryUsage: 0,
    cpuUsage: 0,
    responseTime: 0,
    cacheHitRatio: 0,
    bundleSize: 0,
    loadTime: 0,
  });

  private alertsSubject = new BehaviorSubject<PerformanceAlert[]>([]);
  private startTime = performance.now();

  constructor() {
    this.initializeMonitoring();
  }

  /**
   * Get current performance metrics
   */
  getMetrics(): Observable<PerformanceMetrics> {
    return this.metricsSubject.asObservable();
  }

  /**
   * Get performance alerts
   */
  getAlerts(): Observable<PerformanceAlert[]> {
    return this.alertsSubject.asObservable();
  }

  /**
   * Record response time for API calls
   */
  recordResponseTime(duration: number): void {
    const currentMetrics = this.metricsSubject.value;
    this.metricsSubject.next({
      ...currentMetrics,
      responseTime: duration,
    });

    // Alert if response time is too high
    if (duration > 5000) {
      // 5 seconds
      this.addAlert(
        'error',
        'High response time detected',
        'responseTime',
        duration,
        5000
      );
    } else if (duration > 2000) {
      // 2 seconds
      this.addAlert(
        'warning',
        'Response time is getting high',
        'responseTime',
        duration,
        2000
      );
    }
  }

  /**
   * Update cache hit ratio
   */
  updateCacheHitRatio(ratio: number): void {
    const currentMetrics = this.metricsSubject.value;
    this.metricsSubject.next({
      ...currentMetrics,
      cacheHitRatio: ratio,
    });

    // Alert if cache hit ratio is too low
    if (ratio < 0.3) {
      // 30%
      this.addAlert(
        'warning',
        'Low cache hit ratio',
        'cacheHitRatio',
        ratio,
        0.3
      );
    }
  }

  /**
   * Record bundle size
   */
  recordBundleSize(size: number): void {
    const currentMetrics = this.metricsSubject.value;
    this.metricsSubject.next({
      ...currentMetrics,
      bundleSize: size,
    });

    // Alert if bundle size is too large
    if (size > 2 * 1024 * 1024) {
      // 2MB
      this.addAlert(
        'error',
        'Bundle size is too large',
        'bundleSize',
        size,
        2 * 1024 * 1024
      );
    } else if (size > 1024 * 1024) {
      // 1MB
      this.addAlert(
        'warning',
        'Bundle size is getting large',
        'bundleSize',
        size,
        1024 * 1024
      );
    }
  }

  /**
   * Record page load time
   */
  recordLoadTime(): void {
    const loadTime = performance.now() - this.startTime;
    const currentMetrics = this.metricsSubject.value;
    this.metricsSubject.next({
      ...currentMetrics,
      loadTime,
    });

    // Alert if load time is too high
    if (loadTime > 5000) {
      // 5 seconds
      this.addAlert(
        'error',
        'Page load time is too high',
        'loadTime',
        loadTime,
        5000
      );
    } else if (loadTime > 2000) {
      // 2 seconds
      this.addAlert(
        'warning',
        'Page load time is getting high',
        'loadTime',
        loadTime,
        2000
      );
    }
  }

  /**
   * Get performance score (0-100)
   */
  getPerformanceScore(): Observable<number> {
    return this.metricsSubject.pipe(
      map((metrics) => {
        let score = 100;

        // Deduct points for poor performance
        if (metrics.responseTime > 2000) score -= 20;
        if (metrics.responseTime > 5000) score -= 30;
        if (metrics.cacheHitRatio < 0.5) score -= 15;
        if (metrics.bundleSize > 1024 * 1024) score -= 20;
        if (metrics.loadTime > 3000) score -= 25;

        return Math.max(0, score);
      })
    );
  }

  /**
   * Clear performance alerts
   */
  clearAlerts(): void {
    this.alertsSubject.next([]);
  }

  /**
   * Initialize performance monitoring
   */
  private initializeMonitoring(): void {
    // Monitor memory usage
    interval(30000)
      .pipe(
        // Every 30 seconds
        startWith(0)
      )
      .subscribe(() => {
        this.updateMemoryUsage();
      });

    // Monitor CPU usage (simplified)
    interval(10000)
      .pipe(
        // Every 10 seconds
        startWith(0)
      )
      .subscribe(() => {
        this.updateCpuUsage();
      });
  }

  /**
   * Update memory usage metric
   */
  private updateMemoryUsage(): void {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      const usage = memory.usedJSHeapSize / memory.jsHeapSizeLimit;

      const currentMetrics = this.metricsSubject.value;
      this.metricsSubject.next({
        ...currentMetrics,
        memoryUsage: usage,
      });

      // Alert if memory usage is too high
      if (usage > 0.8) {
        // 80%
        this.addAlert(
          'error',
          'High memory usage detected',
          'memoryUsage',
          usage,
          0.8
        );
      } else if (usage > 0.6) {
        // 60%
        this.addAlert(
          'warning',
          'Memory usage is getting high',
          'memoryUsage',
          usage,
          0.6
        );
      }
    }
  }

  /**
   * Update CPU usage metric (simplified)
   */
  private updateCpuUsage(): void {
    // Simplified CPU usage calculation
    const usage = Math.random() * 0.3; // Simulate 0-30% usage

    const currentMetrics = this.metricsSubject.value;
    this.metricsSubject.next({
      ...currentMetrics,
      cpuUsage: usage,
    });

    // Alert if CPU usage is too high
    if (usage > 0.8) {
      // 80%
      this.addAlert('error', 'High CPU usage detected', 'cpuUsage', usage, 0.8);
    } else if (usage > 0.6) {
      // 60%
      this.addAlert(
        'warning',
        'CPU usage is getting high',
        'cpuUsage',
        usage,
        0.6
      );
    }
  }

  /**
   * Add performance alert
   */
  private addAlert(
    type: 'warning' | 'error',
    message: string,
    metric: keyof PerformanceMetrics,
    value: number,
    threshold: number
  ): void {
    const alert: PerformanceAlert = {
      type,
      message,
      timestamp: new Date(),
      metric,
      value,
      threshold,
    };

    const currentAlerts = this.alertsSubject.value;
    this.alertsSubject.next([...currentAlerts, alert]);

    // Keep only last 10 alerts
    if (currentAlerts.length >= 10) {
      this.alertsSubject.next(currentAlerts.slice(-9));
    }
  }
}
