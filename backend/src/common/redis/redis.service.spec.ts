import { Test, TestingModule } from "@nestjs/testing";
import { RedisService } from "./redis.service";
import { CACHE_MANAGER } from "@nestjs/cache-manager";
import { Cache } from "cache-manager";

// Mock Redis client
jest.mock("redis", () => ({
  createClient: jest.fn(() => ({
    connect: jest.fn(),
    on: jest.fn(),
    hSet: jest.fn(),
    hGet: jest.fn(),
    hGetAll: jest.fn(),
    hDel: jest.fn(),
    lPush: jest.fn(),
    rPop: jest.fn(),
    lRange: jest.fn(),
    sAdd: jest.fn(),
    sMembers: jest.fn(),
    sRem: jest.fn(),
    zAdd: jest.fn(),
    zRange: jest.fn(),
    zRem: jest.fn(),
    exists: jest.fn(),
    expire: jest.fn(),
    ttl: jest.fn(),
    keys: jest.fn(),
    scan: jest.fn(),
    del: jest.fn(),
    hIncrBy: jest.fn(),
    ping: jest.fn(),
    quit: jest.fn(),
  })),
}));

describe("RedisService", () => {
  let service: RedisService;
  let cacheManager: Cache;

  const mockCacheManager = {
    get: jest.fn(),
    set: jest.fn(),
    del: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        RedisService,
        {
          provide: CACHE_MANAGER,
          useValue: mockCacheManager,
        },
      ],
    }).compile();

    service = module.get<RedisService>(RedisService);
    cacheManager = module.get<Cache>(CACHE_MANAGER);
  });

  it("should be defined", () => {
    expect(service).toBeDefined();
  });

  describe("cache operations", () => {
    it("should get value from cache", async () => {
      const key = "test-key";
      const value = "test-value";
      mockCacheManager.get.mockResolvedValue(value);

      const result = await service.get(key);
      expect(result).toBe(value);
      expect(mockCacheManager.get).toHaveBeenCalledWith(key);
    });

    it("should set value in cache", async () => {
      const key = "test-key";
      const value = "test-value";
      const ttl = 3600;

      await service.set(key, value, ttl);
      expect(mockCacheManager.set).toHaveBeenCalledWith(key, value, ttl);
    });

    it("should delete value from cache", async () => {
      const key = "test-key";

      await service.del(key);
      expect(mockCacheManager.del).toHaveBeenCalledWith(key);
    });
  });

  describe("task operations", () => {
    it("should set task status", async () => {
      const taskId = "test-task";
      const status = { id: taskId, status: "running" };

      // Mock Redis client methods
      jest.spyOn(service as any, "hSet").mockResolvedValue(1);
      jest.spyOn(service as any, "expire").mockResolvedValue(1);

      await service.setTaskStatus(taskId, status);
      expect(service["hSet"]).toHaveBeenCalledWith(
        `task:${taskId}`,
        "status",
        JSON.stringify(status)
      );
      expect(service["expire"]).toHaveBeenCalledWith(`task:${taskId}`, 3600);
    });

    it("should get task status", async () => {
      const taskId = "test-task";
      const status = { id: taskId, status: "running" };

      jest
        .spyOn(service as any, "hGet")
        .mockResolvedValue(JSON.stringify(status));

      const result = await service.getTaskStatus(taskId);
      expect(result).toEqual(status);
      expect(service["hGet"]).toHaveBeenCalledWith(`task:${taskId}`, "status");
    });

    it("should set task progress", async () => {
      const taskId = "test-task";
      const progress = 50;

      jest.spyOn(service as any, "hSet").mockResolvedValue(1);

      await service.setTaskProgress(taskId, progress);
      expect(service["hSet"]).toHaveBeenCalledWith(
        `task:${taskId}`,
        "progress",
        progress.toString()
      );
    });

    it("should get task progress", async () => {
      const taskId = "test-task";
      const progress = 50;

      jest.spyOn(service as any, "hGet").mockResolvedValue(progress.toString());

      const result = await service.getTaskProgress(taskId);
      expect(result).toBe(progress);
      expect(service["hGet"]).toHaveBeenCalledWith(
        `task:${taskId}`,
        "progress"
      );
    });
  });
});
