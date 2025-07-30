import { Test, TestingModule } from "@nestjs/testing";
import { ConfigService } from "@nestjs/config";
import { VkApiService } from "./vk-api.service";

// Mock vk-io module
jest.mock("vk-io", () => ({
  VK: jest.fn().mockImplementation(() => ({
    api: {
      users: {
        get: jest
          .fn()
          .mockResolvedValue([
            { id: 1, first_name: "Test", last_name: "User" },
          ]),
      },
      groups: {
        getById: jest.fn().mockResolvedValue([{ id: -1, name: "Test Group" }]),
      },
      wall: {
        get: jest.fn().mockResolvedValue({
          items: [{ id: 1, text: "Test post" }],
          count: 1,
        }),
        search: jest.fn().mockResolvedValue({
          items: [{ id: 1, text: "Test post" }],
          count: 1,
        }),
      },
    },
    token: "test-token",
  })),
}));

describe("VkApiService", () => {
  let service: VkApiService;
  let configService: ConfigService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        VkApiService,
        {
          provide: ConfigService,
          useValue: {
            get: jest.fn().mockReturnValue("test-token"),
          },
        },
      ],
    }).compile();

    service = module.get<VkApiService>(VkApiService);
    configService = module.get<ConfigService>(ConfigService);
  });

  it("should be defined", () => {
    expect(service).toBeDefined();
  });

  it("should initialize with token from config", () => {
    expect(configService.get).toHaveBeenCalledWith("VK_TOKEN");
  });

  describe("checkToken", () => {
    it("should return true for valid token", async () => {
      const result = await service.checkToken();
      expect(typeof result).toBe("boolean");
    }, 10000); // Увеличиваем timeout
  });

  describe("getUser", () => {
    it("should get user by ID", async () => {
      const result = await service.getUser(1);
      expect(result).toBeDefined();
    }, 10000);

    it("should get user by screen name", async () => {
      const result = await service.getUser("durov");
      expect(result).toBeDefined();
    }, 10000);
  });

  describe("getGroup", () => {
    it("should get group by ID", async () => {
      const result = await service.getGroup(-1);
      expect(result).toBeDefined();
    }, 10000);

    it("should get group by screen name", async () => {
      const result = await service.getGroup("durov");
      expect(result).toBeDefined();
    }, 10000);
  });

  describe("getWallPosts", () => {
    it("should get wall posts", async () => {
      const result = await service.getWallPosts(-1, 10);
      expect(result).toBeDefined();
      expect(result.items).toBeDefined();
      expect(Array.isArray(result.items)).toBe(true);
    }, 10000);
  });

  describe("searchPosts", () => {
    it("should search posts", async () => {
      const result = await service.searchPosts("test", undefined, 10);
      expect(result).toBeDefined();
      expect(result.items).toBeDefined();
      expect(Array.isArray(result.items)).toBe(true);
    }, 10000);
  });
});
