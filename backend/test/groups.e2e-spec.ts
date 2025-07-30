import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";
import * as request from "supertest";
import { AppModule } from "../src/app.module";
import { PrismaService } from "../src/prisma/prisma.service";

describe("Groups (e2e)", () => {
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
  });

  afterAll(async () => {
    await prisma.$disconnect();
    await app.close();
  });

  describe("/groups (POST)", () => {
    it("should create a new group", () => {
      const createGroupDto = {
        vkId: 12345,
        screenName: "test_group",
        name: "Test Group",
        description: "Test group description",
      };

      return request(app.getHttpServer())
        .post("/groups")
        .send(createGroupDto)
        .expect(201)
        .expect((res) => {
          expect(res.body).toHaveProperty("id");
          expect(res.body.vkId).toBe(createGroupDto.vkId);
          expect(res.body.screenName).toBe(createGroupDto.screenName);
          expect(res.body.name).toBe(createGroupDto.name);
          expect(res.body.isActive).toBe(true);
        });
    });

    it("should return 400 for duplicate vkId", async () => {
      // Create first group
      await prisma.vKGroup.create({
        data: {
          vkId: 12345,
          screenName: "first_group",
          name: "First Group",
        },
      });

      // Try to create duplicate
      const createGroupDto = {
        vkId: 12345,
        screenName: "second_group",
        name: "Second Group",
      };

      return request(app.getHttpServer())
        .post("/groups")
        .send(createGroupDto)
        .expect(400);
    });

    it("should return 400 for duplicate screenName", async () => {
      // Create first group
      await prisma.vKGroup.create({
        data: {
          vkId: 11111,
          screenName: "test_group",
          name: "First Group",
        },
      });

      // Try to create duplicate
      const createGroupDto = {
        vkId: 22222,
        screenName: "test_group",
        name: "Second Group",
      };

      return request(app.getHttpServer())
        .post("/groups")
        .send(createGroupDto)
        .expect(400);
    });
  });

  describe("/groups (GET)", () => {
    beforeEach(async () => {
      // Create test groups
      await prisma.vKGroup.createMany({
        data: [
          {
            vkId: 11111,
            screenName: "group1",
            name: "Test Group 1",
            description: "First test group",
          },
          {
            vkId: 22222,
            screenName: "group2",
            name: "Test Group 2",
            description: "Second test group",
          },
          {
            vkId: 33333,
            screenName: "group3",
            name: "Another Group",
            description: "Third test group",
          },
        ],
      });
    });

    it("should return all groups with pagination", () => {
      return request(app.getHttpServer())
        .get("/groups?page=1&limit=2")
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

    it("should filter groups by search term", () => {
      return request(app.getHttpServer())
        .get("/groups?search=Test Group")
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(2);
          expect(
            res.body.data.every((g) => g.name.includes("Test Group"))
          ).toBe(true);
        });
    });

    it("should filter by active status", () => {
      return request(app.getHttpServer())
        .get("/groups?isActive=true")
        .expect(200)
        .expect((res) => {
          expect(res.body.data.every((g) => g.isActive === true)).toBe(true);
        });
    });
  });

  describe("/groups/:id (GET)", () => {
    let groupId: string;

    beforeEach(async () => {
      const group = await prisma.vKGroup.create({
        data: {
          vkId: 12345,
          screenName: "test_group",
          name: "Test Group",
          description: "Test group description",
        },
      });
      groupId = group.id.toString();
    });

    it("should return group by id", () => {
      return request(app.getHttpServer())
        .get(`/groups/${groupId}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.id).toBe(groupId);
          expect(res.body.vkId).toBe(12345);
          expect(res.body.screenName).toBe("test_group");
          expect(res.body.name).toBe("Test Group");
        });
    });

    it("should return 404 for non-existent group", () => {
      return request(app.getHttpServer())
        .get("/groups/non-existent-id")
        .expect(404);
    });
  });

  describe("/groups/:id (PUT)", () => {
    let groupId: string;

    beforeEach(async () => {
      const group = await prisma.vKGroup.create({
        data: {
          vkId: 12345,
          screenName: "test_group",
          name: "Test Group",
          description: "Test group description",
        },
      });
      groupId = group.id.toString();
    });

    it("should update group", () => {
      const updateGroupDto = {
        name: "Updated Group Name",
        description: "Updated description",
        isActive: false,
      };

      return request(app.getHttpServer())
        .put(`/groups/${groupId}`)
        .send(updateGroupDto)
        .expect(200)
        .expect((res) => {
          expect(res.body.name).toBe(updateGroupDto.name);
          expect(res.body.description).toBe(updateGroupDto.description);
          expect(res.body.isActive).toBe(updateGroupDto.isActive);
        });
    });

    it("should return 404 for non-existent group", () => {
      return request(app.getHttpServer())
        .put("/groups/non-existent-id")
        .send({ name: "Updated Group" })
        .expect(404);
    });
  });

  describe("/groups/:id (DELETE)", () => {
    let groupId: string;

    beforeEach(async () => {
      const group = await prisma.vKGroup.create({
        data: {
          vkId: 12345,
          screenName: "test_group",
          name: "Test Group",
          description: "Test group description",
        },
      });
      groupId = group.id.toString();
    });

    it("should delete group", () => {
      return request(app.getHttpServer())
        .delete(`/groups/${groupId}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.message).toBe("Group deleted successfully");
        });
    });

    it("should return 404 for non-existent group", () => {
      return request(app.getHttpServer())
        .delete("/groups/non-existent-id")
        .expect(404);
    });
  });

  describe("/groups/bulk (POST)", () => {
    it("should create multiple groups", () => {
      const bulkCreateDto = {
        groups: [
          {
            vkId: 11111,
            screenName: "bulk_group1",
            name: "Bulk Group 1",
          },
          {
            vkId: 22222,
            screenName: "bulk_group2",
            name: "Bulk Group 2",
          },
          {
            vkId: 33333,
            screenName: "bulk_group3",
            name: "Bulk Group 3",
          },
        ],
      };

      return request(app.getHttpServer())
        .post("/groups/bulk")
        .send(bulkCreateDto)
        .expect(201)
        .expect((res) => {
          expect(res.body).toHaveProperty("created");
          expect(res.body).toHaveProperty("skipped");
          expect(res.body.created).toHaveLength(3);
        });
    });

    it("should handle duplicates in bulk create", async () => {
      // Create existing group
      await prisma.vKGroup.create({
        data: {
          vkId: 11111,
          screenName: "existing_group",
          name: "Existing Group",
        },
      });

      const bulkCreateDto = {
        groups: [
          {
            vkId: 11111,
            screenName: "existing_group",
            name: "Existing Group",
          },
          {
            vkId: 22222,
            screenName: "new_group1",
            name: "New Group 1",
          },
          {
            vkId: 33333,
            screenName: "new_group2",
            name: "New Group 2",
          },
        ],
      };

      return request(app.getHttpServer())
        .post("/groups/bulk")
        .send(bulkCreateDto)
        .expect(201)
        .expect((res) => {
          expect(res.body.created).toHaveLength(2);
          expect(res.body.skipped).toHaveLength(1);
        });
    });
  });

  describe("/groups/statistics (GET)", () => {
    beforeEach(async () => {
      // Create test data with posts and comments
      const group1 = await prisma.vKGroup.create({
        data: {
          vkId: 11111,
          screenName: "group1",
          name: "Test Group 1",
        },
      });

      const group2 = await prisma.vKGroup.create({
        data: {
          vkId: 22222,
          screenName: "group2",
          name: "Test Group 2",
        },
      });

      // Create posts for group1
      const post1 = await prisma.vKPost.create({
        data: {
          vkId: 11111,
          groupId: group1.id,
          text: "Post 1",
        },
      });

      const post2 = await prisma.vKPost.create({
        data: {
          vkId: 22222,
          groupId: group1.id,
          text: "Post 2",
        },
      });

      // Create posts for group2
      const post3 = await prisma.vKPost.create({
        data: {
          vkId: 33333,
          groupId: group2.id,
          text: "Post 3",
        },
      });

      // Create comments
      await prisma.vKComment.createMany({
        data: [
          { vkId: 11111, postId: post1.id, text: "Comment 1" },
          { vkId: 22222, postId: post1.id, text: "Comment 2" },
          { vkId: 33333, postId: post2.id, text: "Comment 3" },
          { vkId: 44444, postId: post3.id, text: "Comment 4" },
        ],
      });
    });

    it("should return group statistics", () => {
      return request(app.getHttpServer())
        .get("/groups/statistics")
        .expect(200)
        .expect((res) => {
          expect(res.body).toHaveProperty("totalGroups");
          expect(res.body).toHaveProperty("activeGroups");
          expect(res.body).toHaveProperty("totalPosts");
          expect(res.body).toHaveProperty("totalComments");
          expect(res.body).toHaveProperty("averagePostsPerGroup");
          expect(res.body).toHaveProperty("averageCommentsPerGroup");
        });
    });
  });

  describe("/groups/search (GET)", () => {
    beforeEach(async () => {
      await prisma.vKGroup.createMany({
        data: [
          {
            vkId: 11111,
            screenName: "test_group1",
            name: "Test Group One",
            description: "First test group",
          },
          {
            vkId: 22222,
            screenName: "test_group2",
            name: "Test Group Two",
            description: "Second test group",
          },
          {
            vkId: 33333,
            screenName: "other_group",
            name: "Other Group",
            description: "Different group",
          },
        ],
      });
    });

    it("should search groups by name", () => {
      return request(app.getHttpServer())
        .get("/groups/search?q=Test Group")
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(2);
          expect(
            res.body.data.every((g) => g.name.includes("Test Group"))
          ).toBe(true);
        });
    });

    it("should search groups by screenName", () => {
      return request(app.getHttpServer())
        .get("/groups/search?q=test_group")
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(2);
          expect(
            res.body.data.every((g) => g.screenName.includes("test_group"))
          ).toBe(true);
        });
    });

    it("should return empty results for non-matching search", () => {
      return request(app.getHttpServer())
        .get("/groups/search?q=nonexistent")
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(0);
        });
    });
  });

  describe("/groups/:id/posts (GET)", () => {
    let groupId: string;

    beforeEach(async () => {
      const group = await prisma.vKGroup.create({
        data: {
          vkId: 12345,
          screenName: "test_group",
          name: "Test Group",
        },
      });
      groupId = group.id.toString();

      // Create posts for this group
      await prisma.vKPost.createMany({
        data: [
          {
            vkId: 11111,
            groupId: group.id,
            text: "Post 1",
          },
          {
            vkId: 22222,
            groupId: group.id,
            text: "Post 2",
          },
          {
            vkId: 33333,
            groupId: group.id,
            text: "Post 3",
          },
        ],
      });
    });

    it("should return posts for a specific group", () => {
      return request(app.getHttpServer())
        .get(`/groups/${groupId}/posts`)
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(3);
          expect(res.body.data.every((p) => p.groupId === groupId)).toBe(true);
        });
    });

    it("should return 404 for non-existent group", () => {
      return request(app.getHttpServer())
        .get("/groups/non-existent-id/posts")
        .expect(404);
    });
  });
});
