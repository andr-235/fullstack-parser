import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";
import * as request from "supertest";
import { AppModule } from "../src/app.module";
import { PrismaService } from "../src/prisma/prisma.service";

// Set environment variables for tests
process.env.VK_TOKEN = "test-token";
process.env.DATABASE_URL = "postgresql://test:test@localhost:5432/test_db";

// Mock vk-io globally
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

// Mock ConfigModule
jest.mock("@nestjs/config", () => ({
  ConfigModule: {
    forRoot: jest.fn().mockReturnValue({
      module: class ConfigModule {},
      providers: [],
      exports: [],
    }),
  },
  ConfigService: jest.fn().mockImplementation(() => ({
    get: jest.fn((key: string) => {
      const config = {
        VK_TOKEN: "test-token",
        DATABASE_URL: "postgresql://test:test@localhost:5432/test_db",
        JWT_SECRET: "test-secret",
        PORT: 3000,
      };
      return config[key];
    }),
  })),
}));

// Mock VkApiService
jest.mock("../src/modules/parser/vk-api.service", () => ({
  VkApiService: jest.fn().mockImplementation(() => ({
    getGroup: jest.fn().mockResolvedValue({
      id: -1,
      name: "Test Group",
      screen_name: "test_group",
    }),
    getWallPosts: jest.fn().mockResolvedValue({
      items: [{ id: 1, text: "Test post" }],
      count: 1,
    }),
    getPostComments: jest.fn().mockResolvedValue({
      items: [{ id: 1, text: "Test comment" }],
      count: 1,
    }),
  })),
}));

let app: INestApplication;
let prisma: PrismaService;

beforeAll(async () => {
  const moduleFixture: TestingModule = await Test.createTestingModule({
    imports: [AppModule],
  })
    .overrideProvider("VkApiService")
    .useValue({
      getGroup: jest.fn().mockResolvedValue({
        id: -1,
        name: "Test Group",
        screen_name: "test_group",
      }),
      getWallPosts: jest.fn().mockResolvedValue({
        items: [{ id: 1, text: "Test post" }],
        count: 1,
      }),
      getPostComments: jest.fn().mockResolvedValue({
        items: [{ id: 1, text: "Test comment" }],
        count: 1,
      }),
    })
    .compile();

  app = moduleFixture.createNestApplication();
  await app.init();

  prisma = app.get<PrismaService>(PrismaService);
});

beforeEach(async () => {
  // Clean database before each test
  await prisma.commentKeywordMatch.deleteMany();
  await prisma.vKComment.deleteMany();
  await prisma.vKPost.deleteMany();
  await prisma.vKGroup.deleteMany();
  await prisma.keyword.deleteMany();
});

afterAll(async () => {
  if (prisma) {
    await prisma.$disconnect();
  }
  if (app) {
    await app.close();
  }
});

export { app, prisma, request };
