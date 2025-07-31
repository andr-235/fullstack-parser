import { Injectable } from '@angular/core';
import { Observable, of, BehaviorSubject } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';

export interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number; // Time to live in milliseconds
}

@Injectable({
  providedIn: 'root',
})
export class CacheService {
  private cache = new Map<string, CacheItem<any>>();
  private cacheStats = new BehaviorSubject({
    hits: 0,
    misses: 0,
    size: 0,
  });

  constructor() {
    // Clean up expired cache items every 5 minutes
    setInterval(() => {
      this.cleanupExpired();
    }, 5 * 60 * 1000);
  }

  /**
   * Get data from cache or execute function and cache result
   */
  getOrSet<T>(
    key: string,
    dataFn: () => Observable<T>,
    ttl: number = 5 * 60 * 1000 // 5 minutes default
  ): Observable<T> {
    const cached = this.get<T>(key);

    if (cached) {
      this.cacheStats.next({
        ...this.cacheStats.value,
        hits: this.cacheStats.value.hits + 1,
      });
      return of(cached);
    }

    this.cacheStats.next({
      ...this.cacheStats.value,
      misses: this.cacheStats.value.misses + 1,
    });

    return dataFn().pipe(
      tap((data) => this.set(key, data, ttl)),
      catchError((error) => {
        console.error('Cache error:', error);
        throw error;
      })
    );
  }

  /**
   * Get data from cache
   */
  get<T>(key: string): T | null {
    const item = this.cache.get(key);

    if (!item) {
      return null;
    }

    // Check if item has expired
    if (Date.now() > item.timestamp + item.ttl) {
      this.cache.delete(key);
      this.updateStats();
      return null;
    }

    return item.data;
  }

  /**
   * Set data in cache
   */
  set<T>(key: string, data: T, ttl: number = 5 * 60 * 1000): void {
    const item: CacheItem<T> = {
      data,
      timestamp: Date.now(),
      ttl,
    };

    this.cache.set(key, item);
    this.updateStats();
  }

  /**
   * Remove item from cache
   */
  delete(key: string): void {
    this.cache.delete(key);
    this.updateStats();
  }

  /**
   * Clear all cache
   */
  clear(): void {
    this.cache.clear();
    this.updateStats();
  }

  /**
   * Get cache statistics
   */
  getStats(): Observable<{ hits: number; misses: number; size: number }> {
    return this.cacheStats.asObservable();
  }

  /**
   * Get cache hit ratio
   */
  getHitRatio(): number {
    const stats = this.cacheStats.value;
    const total = stats.hits + stats.misses;
    return total > 0 ? stats.hits / total : 0;
  }

  /**
   * Clean up expired cache items
   */
  private cleanupExpired(): void {
    const now = Date.now();
    let deleted = 0;

    for (const [key, item] of this.cache.entries()) {
      if (now > item.timestamp + item.ttl) {
        this.cache.delete(key);
        deleted++;
      }
    }

    if (deleted > 0) {
      this.updateStats();
      console.log(`Cleaned up ${deleted} expired cache items`);
    }
  }

  /**
   * Update cache statistics
   */
  private updateStats(): void {
    this.cacheStats.next({
      ...this.cacheStats.value,
      size: this.cache.size,
    });
  }

  /**
   * Get cache keys for debugging
   */
  getKeys(): string[] {
    return Array.from(this.cache.keys());
  }

  /**
   * Get cache size
   */
  getSize(): number {
    return this.cache.size;
  }
}
