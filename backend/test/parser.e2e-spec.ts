import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";
import * as request from "supertest";
import { AppModule } from "../src/app.module";
import { PrismaService } from "../src/prisma/prisma.service";

describe("Parser (e2e)", () => {
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
    await prisma.vKComment.deleteMany();
    await prisma.vKPost.deleteMany();
    await prisma.vKGroup.deleteMany();
    await prisma.keyword.deleteMany();
  });

  afterAll(async () => {
    await prisma.$disconnect();
    await app.close();
  });

  describe("/parser/parse-group (POST)", () => {
    it("should parse VK group and return statistics", () => {
      const parseGroupDto = {
        groupId: "test_group",
        limit: 10,
      };

      return request(app.getHttpServer())
        .post("/parser/parse-group")
        .send(parseGroupDto)
        .expect(200)
        .expect((res) => {
          expect(res.body).toHaveProperty("success");
          expect(res.body).toHaveProperty("statistics");
          expect(res.body.statistics).toHaveProperty("postsProcessed");
          expect(res.body.statistics).toHaveProperty("commentsProcessed");
        });
    });

    it("should return 400 for invalid group ID", () => {
      const parseGroupDto = {
        groupId: "",
        limit: 10,
      };

      return request(app.getHttpServer())
        .post("/parser/parse-group")
        .send(parseGroupDto)
        .expect(400);
    });

    it("should return 400 for invalid limit", () => {
      const parseGroupDto = {
        groupId: "test_group",
        limit: -1,
      };

      return request(app.getHttpServer())
        .post("/parser/parse-group")
        .send(parseGroupDto)
        .expect(400);
    });
  });

  describe("/parser/parse-post (POST)", () => {
    beforeEach(async () => {
      // Create a test group first
      await prisma.vKGroup.create({
        data: {
          vkId: 12345,
          screenName: "test_group",
          name: "Test Group",
          description: "Test group description",
        },
      });
    });

    it("should parse VK post and return statistics", () => {
      const parsePostDto = {
        postId: "12345_67890",
        groupId: "test_group",
      };

      return request(app.getHttpServer())
        .post("/parser/parse-post")
        .send(parsePostDto)
        .expect(200)
        .expect((res) => {
          expect(res.body).toHaveProperty("success");
          expect(res.body).toHaveProperty("statistics");
          expect(res.body.statistics).toHaveProperty("commentsProcessed");
        });
    });

    it("should return 400 for invalid post ID", () => {
      const parsePostDto = {
        postId: "",
        groupId: "test_group",
      };

      return request(app.getHttpServer())
        .post("/parser/parse-post")
        .send(parsePostDto)
        .expect(400);
    });
  });

  describe("/parser/statistics (GET)", () => {
    beforeEach(async () => {
      // Create test data
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

      await prisma.vKComment.create({
        data: {
          vkId: 11111,
          postId: post.id,
          text: "Test comment",
        },
      });
    });

    it("should return parsing statistics", () => {
      return request(app.getHttpServer())
        .get("/parser/statistics")
        .expect(200)
        .expect((res) => {
          expect(res.body).toHaveProperty("totalGroups");
          expect(res.body).toHaveProperty("totalPosts");
          expect(res.body).toHaveProperty("totalComments");
          expect(res.body).toHaveProperty("lastParseTime");
        });
    });
  });

  describe("/parser/health (GET)", () => {
    it("should return parser health status", () => {
      return request(app.getHttpServer())
        .get("/parser/health")
        .expect(200)
        .expect((res) => {
          expect(res.body).toHaveProperty("status");
          expect(res.body).toHaveProperty("vkApiStatus");
          expect(res.body).toHaveProperty("databaseStatus");
          expect(res.body.status).toBe("healthy");
        });
    });
  });

  describe("/parser/parse-with-keywords (POST)", () => {
    beforeEach(async () => {
      // Create test keywords
      await prisma.keyword.createMany({
        data: [{ word: "test" }, { word: "important" }, { word: "urgent" }],
      });
    });

    it("should parse group with keyword matching", () => {
      const parseWithKeywordsDto = {
        groupId: "test_group",
        keywords: ["test", "important"],
        limit: 10,
      };

      return request(app.getHttpServer())
        .post("/parser/parse-with-keywords")
        .send(parseWithKeywordsDto)
        .expect(200)
        .expect((res) => {
          expect(res.body).toHaveProperty("success");
          expect(res.body).toHaveProperty("statistics");
          expect(res.body).toHaveProperty("keywordMatches");
          expect(res.body.statistics).toHaveProperty("commentsWithKeywords");
        });
    });

    it("should return 400 for empty keywords array", () => {
      const parseWithKeywordsDto = {
        groupId: "test_group",
        keywords: [],
        limit: 10,
      };

      return request(app.getHttpServer())
        .post("/parser/parse-with-keywords")
        .send(parseWithKeywordsDto)
        .expect(400);
    });
  });
});
