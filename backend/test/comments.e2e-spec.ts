import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";
import { PrismaService } from "../src/prisma/prisma.service";
import { AppModule } from "../src/app.module";
import * as request from "supertest";

describe("Comments (e2e)", () => {
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
    // Clean up database before each test - simplified approach
    await prisma.commentKeywordMatch.deleteMany();
    await prisma.vKComment.deleteMany();
    await prisma.vKPost.deleteMany();
    await prisma.vKGroup.deleteMany();
    await prisma.keyword.deleteMany();
  }, 20000); // Increase timeout to 20 seconds

  afterAll(async () => {
    await prisma.$disconnect();
    await app.close();
  });

  describe("/comments (GET)", () => {
    beforeEach(async () => {
      // Create test data with unique vkId
      const group = await prisma.vKGroup.create({
        data: {
          vkId: Math.floor(Math.random() * 1000000) + 100000,
          screenName: `test_group_1_${Date.now()}`,
          name: "Test Group 1",
        },
      });

      const post = await prisma.vKPost.create({
        data: {
          vkId: Math.floor(Math.random() * 1000000) + 100000,
          groupId: group.id,
          text: "Test post",
        },
      });

      await prisma.vKComment.createMany({
        data: [
          {
            vkId: Math.floor(Math.random() * 1000000) + 100000,
            postId: post.id,
            text: "First test comment",
          },
          {
            vkId: Math.floor(Math.random() * 1000000) + 200000,
            postId: post.id,
            text: "Second test comment",
          },
          {
            vkId: Math.floor(Math.random() * 1000000) + 300000,
            postId: post.id,
            text: "Third test comment",
          },
        ],
      });
    });

    it("should return all comments with pagination", () => {
      return request(app.getHttpServer())
        .get("/comments?page=1&limit=2")
        .expect(200)
        .expect((res) => {
          expect(res.body).toHaveProperty("comments");
          expect(res.body).toHaveProperty("total");
          expect(res.body).toHaveProperty("page");
          expect(res.body).toHaveProperty("limit");
          expect(res.body.comments).toHaveLength(2);
          expect(res.body.total).toBe(3);
        });
    });

    it("should filter comments by search term", () => {
      return request(app.getHttpServer())
        .get("/comments?search=First")
        .expect(200)
        .expect((res) => {
          expect(res.body.comments).toHaveLength(1);
          expect(res.body.comments[0].text).toBe("First test comment");
        });
    });

    it("should filter comments by group", async () => {
      const group = await prisma.vKGroup.findFirst();

      return request(app.getHttpServer())
        .get(`/comments?groupId=${group.id}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.comments).toHaveLength(3);
        });
    });

    it("should filter comments by post", async () => {
      const post = await prisma.vKPost.findFirst();

      return request(app.getHttpServer())
        .get(`/comments?postId=${post.id}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.comments).toHaveLength(3);
        });
    });
  });

  describe("/comments/:id (GET)", () => {
    let commentId: string;

    beforeEach(async () => {
      const group = await prisma.vKGroup.create({
        data: {
          vkId: 12346,
          screenName: "test_group_2",
          name: "Test Group 2",
        },
      });

      const post = await prisma.vKPost.create({
        data: {
          vkId: 67891,
          groupId: group.id,
          text: "Test post for single comment",
        },
      });

      const comment = await prisma.vKComment.create({
        data: {
          vkId: 11112,
          postId: post.id,
          text: "Single test comment",
        },
      });

      commentId = comment.id.toString();
    });

    it("should return comment by id", () => {
      return request(app.getHttpServer())
        .get(`/comments/${commentId}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.id).toBe(commentId);
          expect(res.body.text).toBe("Single test comment");
        });
    });

    it("should return 404 for non-existent comment", () => {
      return request(app.getHttpServer())
        .get("/comments/non-existent-id")
        .expect(404);
    });
  });

  describe("/comments/statistics (GET)", () => {
    beforeEach(async () => {
      // Create test data with unique vkId
      const group = await prisma.vKGroup.create({
        data: {
          vkId: 12349,
          screenName: "test_group_5",
          name: "Test Group 5",
        },
      });

      const post = await prisma.vKPost.create({
        data: {
          vkId: 67894,
          groupId: group.id,
          text: "Test post for statistics",
        },
      });

      await prisma.vKComment.createMany({
        data: [
          {
            vkId: 11115,
            postId: post.id,
            text: "Comment 1",
          },
          {
            vkId: 11116,
            postId: post.id,
            text: "Comment 2",
          },
        ],
      });
    });

    it("should return comment statistics", () => {
      return request(app.getHttpServer())
        .get("/comments/statistics")
        .expect(200)
        .expect((res) => {
          expect(res.body).toHaveProperty("totalComments");
          expect(res.body).toHaveProperty("commentsWithKeywords");
          expect(res.body).toHaveProperty("averageCommentsPerPost");
        });
    });
  });

  afterAll(async () => {
    await prisma.$disconnect();
    await new Promise((resolve) => setTimeout(resolve, 1000)); // Wait for connections to close
  });
});
