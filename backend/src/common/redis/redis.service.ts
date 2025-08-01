import { Injectable, Inject } from "@nestjs/common";
import { CACHE_MANAGER } from "@nestjs/cache-manager";
import { Cache } from "cache-manager";
import Redis from "ioredis";

@Injectable()
export class RedisService {
  private redisClient: Redis;

  constructor(@Inject(CACHE_MANAGER) private cacheManager: Cache) {
    this.initRedisClient();
  }

  private async initRedisClient() {
    this.redisClient = new Redis({
      host: process.env.REDIS_HOST || "redis",
      port: parseInt(process.env.REDIS_PORT || "6379"),
      password: process.env.REDIS_PASSWORD,
      db: parseInt(process.env.REDIS_DB || "0"),
      retryDelayOnFailover: 100,
      maxRetriesPerRequest: 3,
      lazyConnect: true,
    } as any);

    this.redisClient.on("error", (err) => {
      console.error("Redis Client Error:", err);
    });

    this.redisClient.on("connect", () => {
      console.log("Redis Client Connected");
    });

    this.redisClient.on("ready", () => {
      console.log("Redis Client Ready");
    });

    this.redisClient.on("reconnecting", () => {
      console.log("Redis Client Reconnecting...");
    });

    await this.redisClient.connect();
  }

  // Cache operations
  async get(key: string): Promise<any> {
    return this.cacheManager.get(key);
  }

  async set(key: string, value: any, ttl?: number): Promise<void> {
    await this.cacheManager.set(key, value, ttl);
  }

  async del(key: string): Promise<void> {
    await this.cacheManager.del(key);
  }

  async clear(): Promise<void> {
    console.log("Cache clear not implemented");
    // Note: cache-manager v5 might not have a direct reset method
    // You might need to implement a custom clear method
  }

  // Direct Redis operations
  async hSet(key: string, field: string, value: string): Promise<number> {
    return this.redisClient.hset(key, field, value);
  }

  async hGet(key: string, field: string): Promise<string | null> {
    const result = await this.redisClient.hget(key, field);
    return result;
  }

  async hGetAll(key: string): Promise<Record<string, string>> {
    return this.redisClient.hgetall(key);
  }

  async hDel(key: string, ...fields: string[]): Promise<number> {
    return this.redisClient.hdel(key, ...fields);
  }

  async lPush(key: string, ...values: string[]): Promise<number> {
    return this.redisClient.lpush(key, ...values);
  }

  async rPop(key: string): Promise<string | null> {
    const result = await this.redisClient.rpop(key);
    return result;
  }

  async lRange(key: string, start: number, stop: number): Promise<string[]> {
    return this.redisClient.lrange(key, start, stop);
  }

  async sAdd(key: string, ...members: string[]): Promise<number> {
    return this.redisClient.sadd(key, ...members);
  }

  async sMembers(key: string): Promise<string[]> {
    return this.redisClient.smembers(key);
  }

  async sRem(key: string, ...members: string[]): Promise<number> {
    return this.redisClient.srem(key, ...members);
  }

  async zAdd(key: string, score: number, member: string): Promise<number> {
    return this.redisClient.zadd(key, score, member);
  }

  async zRange(key: string, start: number, stop: number): Promise<string[]> {
    return this.redisClient.zrange(key, start, stop);
  }

  async zRem(key: string, ...members: string[]): Promise<number> {
    return this.redisClient.zrem(key, ...members);
  }

  async exists(key: string): Promise<number> {
    return this.redisClient.exists(key);
  }

  async expire(key: string, seconds: number): Promise<number> {
    return this.redisClient.expire(key, seconds);
  }

  async ttl(key: string): Promise<number> {
    return this.redisClient.ttl(key);
  }

  async keys(pattern: string): Promise<string[]> {
    return this.redisClient.keys(pattern);
  }

  async scan(
    cursor: number,
    pattern: string,
    count: number = 10
  ): Promise<[number, string[]]> {
    const result = await this.redisClient.scan(
      cursor,
      "MATCH",
      pattern,
      "COUNT",
      count
    );
    return [parseInt(result[0]), result[1]];
  }

  async deleteKeys(...keys: string[]): Promise<number> {
    return this.redisClient.del(...keys);
  }

  async hIncrBy(
    key: string,
    field: string,
    increment: number
  ): Promise<number> {
    return this.redisClient.hincrby(key, field, increment);
  }

  async ping(): Promise<string> {
    return this.redisClient.ping();
  }

  async quit(): Promise<void> {
    await this.redisClient.quit();
  }

  // Task-specific methods
  async setTaskStatus(taskId: string, status: any): Promise<void> {
    await this.hSet(`task:${taskId}`, "status", JSON.stringify(status));
  }

  async getTaskStatus(taskId: string): Promise<any> {
    const status = await this.hGet(`task:${taskId}`, "status");
    return status ? JSON.parse(status) : null;
  }

  async setTaskProgress(taskId: string, progress: number): Promise<void> {
    await this.hSet(`task:${taskId}`, "progress", progress.toString());
  }

  async getTaskProgress(taskId: string): Promise<number> {
    const progress = await this.hGet(`task:${taskId}`, "progress");
    return progress ? parseInt(progress) : 0;
  }

  async addTaskToQueue(taskId: string): Promise<void> {
    await this.lPush("task_queue", taskId);
  }

  async getNextTask(): Promise<string | null> {
    return await this.rPop("task_queue");
  }

  async setCurrentGroup(taskId: string, groupName: string): Promise<void> {
    await this.hSet(`task:${taskId}`, "currentGroup", groupName);
  }

  async incrementProcessedGroups(taskId: string): Promise<number> {
    return await this.hIncrBy(`task:${taskId}`, "processedGroups", 1);
  }

  async setTaskError(taskId: string, error: string): Promise<void> {
    await this.hSet(`task:${taskId}`, "error", error);
  }

  async setTaskResults(taskId: string, results: any): Promise<void> {
    await this.hSet(`task:${taskId}`, "results", JSON.stringify(results));
  }

  async setTaskCompletedAt(taskId: string, completedAt: Date): Promise<void> {
    await this.hSet(`task:${taskId}`, "completedAt", completedAt.toISOString());
  }

  async cleanupTask(taskId: string): Promise<void> {
    await this.deleteKeys(`task:${taskId}`);
  }

  async cleanupExpiredTasks(): Promise<void> {
    const taskKeys = await this.keys("task:*");
    const now = Date.now();
    const expireTime = 24 * 60 * 60 * 1000; // 24 hours

    for (const key of taskKeys) {
      const taskData = await this.hGetAll(key);
      const createdAt = taskData.createdAt
        ? new Date(taskData.createdAt).getTime()
        : 0;

      if (now - createdAt > expireTime) {
        await this.deleteKeys(key);
      }
    }
  }
}
