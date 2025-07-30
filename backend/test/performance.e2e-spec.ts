import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";
import * as request from "supertest";
import { AppModule } from "../src/app.module";
import { PrismaService } from "../src/prisma/prisma.service";

describe("Performance (e2e)", () => {
  let app: INestApplication;
  let prisma: PrismaService;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    prisma = app.get<PrismaService>(PrismaService);

    await app.init();
  });

  beforeEach(async () => {
    // Clean up database before each test
    await prisma.commentKeywordMatch.deleteMany();
    await prisma.vKComment.deleteMany();
    await prisma.vKPost.deleteMany();
    await prisma.vKGroup.deleteMany();
    await prisma.keyword.deleteMany();
    await prisma.user.deleteMany();
  });

  afterAll(async () => {
    await prisma.$disconnect();
    await app.close();
  });

  describe("Bulk Operations Performance", () => {
    it("should handle bulk keyword creation efficiently", async () => {
      const startTime = Date.now();

      const bulkCreateDto = {
        words: Array.from({ length: 100 }, (_, i) => `keyword_${i}`),
      };

      const response = await request(app.getHttpServer())
        .post("/keywords/bulk")
        .send(bulkCreateDto)
        .expect(201);

      const endTime = Date.now();
      const duration = endTime - startTime;

      expect(response.body.created).toHaveLength(100);
      expect(duration).toBeLessThan(5000); // Should complete within 5 seconds
    });

    it("should handle bulk group creation efficiently", async () => {
      const startTime = Date.now();

      const bulkCreateDto = {
        groups: Array.from({ length: 50 }, (_, i) => ({
          vkId: 10000 + i,
          screenName: `group_${i}`,
          name: `Test Group ${i}`,
          description: `Description for group ${i}`,
        })),
      };

      const response = await request(app.getHttpServer())
        .post("/groups/bulk")
        .send(bulkCreateDto)
        .expect(201);

      const endTime = Date.now();
      const duration = endTime - startTime;

      expect(response.body.created).toHaveLength(50);
      expect(duration).toBeLessThan(3000); // Should complete within 3 seconds
    });
  });

  describe("Search Performance", () => {
    beforeEach(async () => {
      // Create test data for search performance tests
      await prisma.keyword.createMany({
        data: Array.from({ length: 1000 }, (_, i) => ({
          word: `keyword_${i}_${Math.random().toString(36).substring(7)}`,
        })),
      });

      await prisma.vKGroup.createMany({
        data: Array.from({ length: 100 }, (_, i) => ({
          vkId: 10000 + i,
          screenName: `group_${i}`,
          name: `Test Group ${i}`,
          description: `Description for group ${i}`,
        })),
      });
    });

    it("should perform keyword search efficiently", async () => {
      const startTime = Date.now();

      const response = await request(app.getHttpServer())
        .get("/keywords/search?q=keyword_50")
        .expect(200);

      const endTime = Date.now();
      const duration = endTime - startTime;

      expect(response.body.data.length).toBeGreaterThan(0);
      expect(duration).toBeLessThan(1000); // Should complete within 1 second
    });

    it("should perform group search efficiently", async () => {
      const startTime = Date.now();

      const response = await request(app.getHttpServer())
        .get("/groups/search?q=Test Group")
        .expect(200);

      const endTime = Date.now();
      const duration = endTime - startTime;

      expect(response.body.data.length).toBeGreaterThan(0);
      expect(duration).toBeLessThan(1000); // Should complete within 1 second
    });
  });

  describe("Statistics Performance", () => {
    beforeEach(async () => {
      // Create comprehensive test data
      const groups = await prisma.vKGroup.createMany({
        data: Array.from({ length: 10 }, (_, i) => ({
          vkId: 10000 + i,
          screenName: `group_${i}`,
          name: `Test Group ${i}`,
        })),
      });

      const createdGroups = await prisma.vKGroup.findMany();

      // Create posts for each group
      for (const group of createdGroups) {
        await prisma.vKPost.createMany({
          data: Array.from({ length: 20 }, (_, i) => ({
            vkId: 20000 + group.vkId + i,
            groupId: group.id,
            text: `Post ${i} for group ${group.id}`,
          })),
        });
      }

      const posts = await prisma.vKPost.findMany();

      // Create comments for each post
      for (const post of posts) {
        await prisma.vKComment.createMany({
          data: Array.from({ length: 5 }, (_, i) => ({
            vkId: 30000 + post.vkId + i,
            postId: post.id,
            text: `Comment ${i} for post ${post.id}`,
          })),
        });
      }
    });

    it("should calculate statistics efficiently", async () => {
      const startTime = Date.now();

      const response = await request(app.getHttpServer())
        .get("/groups/statistics")
        .expect(200);

      const endTime = Date.now();
      const duration = endTime - startTime;

      expect(response.body).toHaveProperty("totalGroups");
      expect(response.body).toHaveProperty("totalPosts");
      expect(response.body).toHaveProperty("totalComments");
      expect(duration).toBeLessThan(2000); // Should complete within 2 seconds
    });

    it("should calculate keyword statistics efficiently", async () => {
      // Create keywords and matches
      const keywords = await prisma.keyword.createMany({
        data: Array.from({ length: 50 }, (_, i) => ({
          word: `keyword_${i}`,
        })),
      });

      const createdKeywords = await prisma.keyword.findMany();
      const comments = await prisma.vKComment.findMany();

      // Create some keyword matches
      for (let i = 0; i < Math.min(comments.length, 100); i++) {
        await prisma.commentKeywordMatch.create({
          data: {
            commentId: comments[i].id,
            keywordId: createdKeywords[i % createdKeywords.length].id,
          },
        });
      }

      const startTime = Date.now();

      const response = await request(app.getHttpServer())
        .get("/keywords/statistics")
        .expect(200);

      const endTime = Date.now();
      const duration = endTime - startTime;

      expect(response.body).toHaveProperty("totalKeywords");
      expect(response.body).toHaveProperty("totalMatches");
      expect(duration).toBeLessThan(2000); // Should complete within 2 seconds
    });
  });

  describe("Concurrent Requests Performance", () => {
    beforeEach(async () => {
      // Create test data
      await prisma.keyword.createMany({
        data: Array.from({ length: 100 }, (_, i) => ({
          word: `keyword_${i}`,
        })),
      });

      await prisma.vKGroup.createMany({
        data: Array.from({ length: 50 }, (_, i) => ({
          vkId: 10000 + i,
          screenName: `group_${i}`,
          name: `Test Group ${i}`,
        })),
      });
    });

    it("should handle concurrent GET requests efficiently", async () => {
      const startTime = Date.now();

      // Make concurrent requests
      const promises = [
        request(app.getHttpServer()).get("/keywords?page=1&limit=10"),
        request(app.getHttpServer()).get("/groups?page=1&limit=10"),
        request(app.getHttpServer()).get("/keywords/search?q=keyword"),
        request(app.getHttpServer()).get("/groups/search?q=Test"),
        request(app.getHttpServer()).get("/keywords/statistics"),
        request(app.getHttpServer()).get("/groups/statistics"),
      ];

      const responses = await Promise.all(promises);
      const endTime = Date.now();
      const duration = endTime - startTime;

      // All requests should succeed
      responses.forEach((response) => {
        expect(response.status).toBe(200);
      });

      expect(duration).toBeLessThan(3000); // Should complete within 3 seconds
    });

    it("should handle concurrent POST requests efficiently", async () => {
      const startTime = Date.now();

      // Make concurrent creation requests
      const promises = [
        request(app.getHttpServer())
          .post("/keywords")
          .send({ word: "concurrent_keyword_1" }),
        request(app.getHttpServer())
          .post("/keywords")
          .send({ word: "concurrent_keyword_2" }),
        request(app.getHttpServer()).post("/groups").send({
          vkId: 20001,
          screenName: "concurrent_group_1",
          name: "Concurrent Group 1",
        }),
        request(app.getHttpServer()).post("/groups").send({
          vkId: 20002,
          screenName: "concurrent_group_2",
          name: "Concurrent Group 2",
        }),
      ];

      const responses = await Promise.all(promises);
      const endTime = Date.now();
      const duration = endTime - startTime;

      // All requests should succeed
      responses.forEach((response) => {
        expect(response.status).toBe(201);
      });

      expect(duration).toBeLessThan(2000); // Should complete within 2 seconds
    });
  });

  describe("Memory Usage Performance", () => {
    it("should not leak memory during bulk operations", async () => {
      const initialMemory = process.memoryUsage().heapUsed;

      // Perform multiple bulk operations
      for (let i = 0; i < 5; i++) {
        await request(app.getHttpServer())
          .post("/keywords/bulk")
          .send({
            words: Array.from(
              { length: 100 },
              (_, j) => `bulk_keyword_${i}_${j}`
            ),
          })
          .expect(201);
      }

      const finalMemory = process.memoryUsage().heapUsed;
      const memoryIncrease = finalMemory - initialMemory;

      // Memory increase should be reasonable (less than 50MB)
      expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024);
    });
  });
});
