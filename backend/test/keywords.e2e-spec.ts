import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";
import * as request from "supertest";
import { AppModule } from "../src/app.module";
import { PrismaService } from "../src/prisma/prisma.service";

describe("Keywords (e2e)", () => {
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
    await prisma.keyword.deleteMany();
  });

  afterAll(async () => {
    await prisma.$disconnect();
    await app.close();
  });

  describe("/keywords (POST)", () => {
    it("should create a new keyword", () => {
      const createKeywordDto = {
        word: "test_keyword",
      };

      return request(app.getHttpServer())
        .post("/keywords")
        .send(createKeywordDto)
        .expect(201)
        .expect((res) => {
          expect(res.body).toHaveProperty("id");
          expect(res.body.word).toBe(createKeywordDto.word);
          expect(res.body.isActive).toBe(true);
        });
    });

    it("should return 400 for empty word", () => {
      const createKeywordDto = {
        word: "",
      };

      return request(app.getHttpServer())
        .post("/keywords")
        .send(createKeywordDto)
        .expect(400);
    });

    it("should return 400 for duplicate keyword", async () => {
      // Create first keyword
      await prisma.keyword.create({
        data: { word: "duplicate_keyword" },
      });

      // Try to create duplicate
      const createKeywordDto = {
        word: "duplicate_keyword",
      };

      return request(app.getHttpServer())
        .post("/keywords")
        .send(createKeywordDto)
        .expect(400);
    });
  });

  describe("/keywords (GET)", () => {
    beforeEach(async () => {
      // Create test keywords
      await prisma.keyword.createMany({
        data: [
          { word: "test1" },
          { word: "test2" },
          { word: "important" },
          { word: "urgent" },
        ],
      });
    });

    it("should return all keywords with pagination", () => {
      return request(app.getHttpServer())
        .get("/keywords?page=1&limit=2")
        .expect(200)
        .expect((res) => {
          expect(res.body).toHaveProperty("data");
          expect(res.body).toHaveProperty("total");
          expect(res.body).toHaveProperty("page");
          expect(res.body).toHaveProperty("limit");
          expect(res.body.data).toHaveLength(2);
          expect(res.body.total).toBe(4);
        });
    });

    it("should filter keywords by search term", () => {
      return request(app.getHttpServer())
        .get("/keywords?search=test")
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(2);
          expect(res.body.data.every((k) => k.word.includes("test"))).toBe(
            true
          );
        });
    });

    it("should filter by active status", () => {
      return request(app.getHttpServer())
        .get("/keywords?isActive=true")
        .expect(200)
        .expect((res) => {
          expect(res.body.data.every((k) => k.isActive === true)).toBe(true);
        });
    });
  });

  describe("/keywords/:id (GET)", () => {
    let keywordId: string;

    beforeEach(async () => {
      const keyword = await prisma.keyword.create({
        data: { word: "test_keyword" },
      });
      keywordId = keyword.id;
    });

    it("should return keyword by id", () => {
      return request(app.getHttpServer())
        .get(`/keywords/${keywordId}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.id).toBe(keywordId);
          expect(res.body.word).toBe("test_keyword");
        });
    });

    it("should return 404 for non-existent keyword", () => {
      return request(app.getHttpServer())
        .get("/keywords/non-existent-id")
        .expect(404);
    });
  });

  describe("/keywords/:id (PUT)", () => {
    let keywordId: string;

    beforeEach(async () => {
      const keyword = await prisma.keyword.create({
        data: { word: "test_keyword" },
      });
      keywordId = keyword.id;
    });

    it("should update keyword", () => {
      const updateKeywordDto = {
        word: "updated_keyword",
        isActive: false,
      };

      return request(app.getHttpServer())
        .put(`/keywords/${keywordId}`)
        .send(updateKeywordDto)
        .expect(200)
        .expect((res) => {
          expect(res.body.word).toBe(updateKeywordDto.word);
          expect(res.body.isActive).toBe(updateKeywordDto.isActive);
        });
    });

    it("should return 404 for non-existent keyword", () => {
      return request(app.getHttpServer())
        .put("/keywords/non-existent-id")
        .send({ word: "updated_keyword" })
        .expect(404);
    });
  });

  describe("/keywords/:id (DELETE)", () => {
    let keywordId: string;

    beforeEach(async () => {
      const keyword = await prisma.keyword.create({
        data: { word: "test_keyword" },
      });
      keywordId = keyword.id;
    });

    it("should delete keyword", () => {
      return request(app.getHttpServer())
        .delete(`/keywords/${keywordId}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.message).toBe("Keyword deleted successfully");
        });
    });

    it("should return 404 for non-existent keyword", () => {
      return request(app.getHttpServer())
        .delete("/keywords/non-existent-id")
        .expect(404);
    });
  });

  describe("/keywords/bulk (POST)", () => {
    it("should create multiple keywords", () => {
      const bulkCreateDto = {
        words: ["bulk1", "bulk2", "bulk3"],
      };

      return request(app.getHttpServer())
        .post("/keywords/bulk")
        .send(bulkCreateDto)
        .expect(201)
        .expect((res) => {
          expect(res.body).toHaveProperty("created");
          expect(res.body).toHaveProperty("skipped");
          expect(res.body.created).toHaveLength(3);
        });
    });

    it("should handle duplicates in bulk create", async () => {
      // Create existing keyword
      await prisma.keyword.create({
        data: { word: "existing_keyword" },
      });

      const bulkCreateDto = {
        words: ["existing_keyword", "new_keyword1", "new_keyword2"],
      };

      return request(app.getHttpServer())
        .post("/keywords/bulk")
        .send(bulkCreateDto)
        .expect(201)
        .expect((res) => {
          expect(res.body.created).toHaveLength(2);
          expect(res.body.skipped).toHaveLength(1);
        });
    });
  });

  describe("/keywords/statistics (GET)", () => {
    beforeEach(async () => {
      // Create test data with keyword matches
      const keyword1 = await prisma.keyword.create({ data: { word: "test" } });
      const keyword2 = await prisma.keyword.create({
        data: { word: "important" },
      });

      const group = await prisma.vKGroup.create({
        data: {
          vkId: 12345,
          screenName: "test_group",
          name: "Test Group",
        },
      });

      const post = await prisma.vKPost.create({
        data: {
          vkId: 67890,
          groupId: group.id,
          text: "Test post",
        },
      });

      const comment = await prisma.vKComment.create({
        data: {
          vkId: 11111,
          postId: post.id,
          text: "This is a test comment with important information",
        },
      });

      // Create keyword matches
      await prisma.commentKeywordMatch.createMany({
        data: [
          { commentId: comment.id, keywordId: keyword1.id },
          { commentId: comment.id, keywordId: keyword2.id },
        ],
      });
    });

    it("should return keyword statistics", () => {
      return request(app.getHttpServer())
        .get("/keywords/statistics")
        .expect(200)
        .expect((res) => {
          expect(res.body).toHaveProperty("totalKeywords");
          expect(res.body).toHaveProperty("activeKeywords");
          expect(res.body).toHaveProperty("totalMatches");
          expect(res.body).toHaveProperty("topKeywords");
        });
    });
  });

  describe("/keywords/search (GET)", () => {
    beforeEach(async () => {
      await prisma.keyword.createMany({
        data: [
          { word: "test_keyword" },
          { word: "important_test" },
          { word: "urgent_matter" },
          { word: "test_case" },
        ],
      });
    });

    it("should search keywords by word", () => {
      return request(app.getHttpServer())
        .get("/keywords/search?q=test")
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(3);
          expect(res.body.data.every((k) => k.word.includes("test"))).toBe(
            true
          );
        });
    });

    it("should return empty results for non-matching search", () => {
      return request(app.getHttpServer())
        .get("/keywords/search?q=nonexistent")
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(0);
        });
    });
  });
});
