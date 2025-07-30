import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";
import * as request from "supertest";
import { AppModule } from "../src/app.module";
import { PrismaService } from "../src/prisma/prisma.service";

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
    // Clean up database before each test
    await prisma.commentKeywordMatch.deleteMany();
    await prisma.vKComment.deleteMany();
    await prisma.vKPost.deleteMany();
    await prisma.vKGroup.deleteMany();
    await prisma.keyword.deleteMany();
  });

  afterAll(async () => {
    await prisma.$disconnect();
    await app.close();
  });

  describe("/comments (GET)", () => {
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

      await prisma.vKComment.createMany({
        data: [
          {
            vkId: 11111,
            postId: post.id,
            text: "First test comment",
          },
          {
            vkId: 22222,
            postId: post.id,
            text: "Second test comment",
          },
          {
            vkId: 33333,
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
          expect(res.body).toHaveProperty("data");
          expect(res.body).toHaveProperty("total");
          expect(res.body).toHaveProperty("page");
          expect(res.body).toHaveProperty("limit");
          expect(res.body.data).toHaveLength(2);
          expect(res.body.total).toBe(3);
        });
    });

    it("should filter comments by search term", () => {
      return request(app.getHttpServer())
        .get("/comments?search=First")
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(1);
          expect(res.body.data[0].text).toBe("First test comment");
        });
    });

    it("should filter comments by group", async () => {
      const group = await prisma.vKGroup.findFirst();

      return request(app.getHttpServer())
        .get(`/comments?groupId=${group.id}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(3);
        });
    });

    it("should filter comments by post", async () => {
      const post = await prisma.vKPost.findFirst();

      return request(app.getHttpServer())
        .get(`/comments?postId=${post.id}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(3);
        });
    });
  });

  describe("/comments/:id (GET)", () => {
    let commentId: string;

    beforeEach(async () => {
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
          text: "Test comment",
        },
      });
      commentId = comment.id;
    });

    it("should return comment by id", () => {
      return request(app.getHttpServer())
        .get(`/comments/${commentId}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.id).toBe(commentId);
          expect(res.body.text).toBe("Test comment");
          expect(res.body.vkId).toBe(11111);
        });
    });

    it("should return 404 for non-existent comment", () => {
      return request(app.getHttpServer())
        .get("/comments/non-existent-id")
        .expect(404);
    });
  });

  describe("/comments/:id (PUT)", () => {
    let commentId: string;

    beforeEach(async () => {
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
          text: "Test comment",
        },
      });
      commentId = comment.id;
    });

    it("should update comment", () => {
      const updateCommentDto = {
        text: "Updated comment text",
      };

      return request(app.getHttpServer())
        .put(`/comments/${commentId}`)
        .send(updateCommentDto)
        .expect(200)
        .expect((res) => {
          expect(res.body.text).toBe(updateCommentDto.text);
        });
    });

    it("should return 404 for non-existent comment", () => {
      return request(app.getHttpServer())
        .put("/comments/non-existent-id")
        .send({ text: "Updated comment" })
        .expect(404);
    });
  });

  describe("/comments/:id (DELETE)", () => {
    let commentId: string;

    beforeEach(async () => {
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
          text: "Test comment",
        },
      });
      commentId = comment.id;
    });

    it("should delete comment", () => {
      return request(app.getHttpServer())
        .delete(`/comments/${commentId}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.message).toBe("Comment deleted successfully");
        });
    });

    it("should return 404 for non-existent comment", () => {
      return request(app.getHttpServer())
        .delete("/comments/non-existent-id")
        .expect(404);
    });
  });

  describe("/comments/statistics (GET)", () => {
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

      await prisma.vKComment.createMany({
        data: [
          {
            vkId: 11111,
            postId: post.id,
            text: "First comment",
          },
          {
            vkId: 22222,
            postId: post.id,
            text: "Second comment",
          },
          {
            vkId: 33333,
            postId: post.id,
            text: "Third comment",
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
          expect(res.body).toHaveProperty("commentsByGroup");
          expect(res.body).toHaveProperty("commentsByPost");
          expect(res.body).toHaveProperty("averageCommentsPerPost");
        });
    });
  });

  describe("/comments/search (GET)", () => {
    beforeEach(async () => {
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

      await prisma.vKComment.createMany({
        data: [
          {
            vkId: 11111,
            postId: post.id,
            text: "Important comment about test",
          },
          {
            vkId: 22222,
            postId: post.id,
            text: "Another test comment",
          },
          {
            vkId: 33333,
            postId: post.id,
            text: "Regular comment",
          },
        ],
      });
    });

    it("should search comments by text", () => {
      return request(app.getHttpServer())
        .get("/comments/search?q=test")
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(2);
          expect(res.body.data.every((c) => c.text.includes("test"))).toBe(
            true
          );
        });
    });

    it("should return empty results for non-matching search", () => {
      return request(app.getHttpServer())
        .get("/comments/search?q=nonexistent")
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(0);
        });
    });
  });

  describe("/comments/with-keywords (GET)", () => {
    beforeEach(async () => {
      // Create test data with keyword matches
      const keyword = await prisma.keyword.create({
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
          text: "This is an important comment",
        },
      });

      // Create keyword match
      await prisma.commentKeywordMatch.create({
        data: {
          commentId: comment.id,
          keywordId: keyword.id,
        },
      });
    });

    it("should return comments with keyword matches", () => {
      return request(app.getHttpServer())
        .get("/comments/with-keywords")
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(1);
          expect(res.body.data[0].text).toBe("This is an important comment");
        });
    });

    it("should filter by specific keyword", () => {
      return request(app.getHttpServer())
        .get("/comments/with-keywords?keyword=important")
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(1);
        });
    });
  });
});
