import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";
import * as request from "supertest";
import { AppModule } from "../src/app.module";
import { PrismaService } from "../src/prisma/prisma.service";

describe("Users (e2e)", () => {
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
    await prisma.user.deleteMany();
  });

  afterAll(async () => {
    await prisma.$disconnect();
    await app.close();
  });

  describe("/users (POST)", () => {
    it("should create a new user", () => {
      const createUserDto = {
        email: "test@example.com",
        fullName: "Test User",
        password: "password123",
      };

      return request(app.getHttpServer())
        .post("/users")
        .send(createUserDto)
        .expect(201)
        .expect((res) => {
          expect(res.body).toHaveProperty("id");
          expect(res.body.email).toBe(createUserDto.email);
          expect(res.body.fullName).toBe(createUserDto.fullName);
          expect(res.body).not.toHaveProperty("password");
        });
    });

    it("should return 400 for invalid email", () => {
      const createUserDto = {
        email: "invalid-email",
        fullName: "Test User",
        password: "password123",
      };

      return request(app.getHttpServer())
        .post("/users")
        .send(createUserDto)
        .expect(400);
    });

    it("should return 400 for missing required fields", () => {
      const createUserDto = {
        email: "test@example.com",
        // Missing fullName and password
      };

      return request(app.getHttpServer())
        .post("/users")
        .send(createUserDto)
        .expect(400);
    });
  });

  describe("/users (GET)", () => {
    beforeEach(async () => {
      // Create test users
      await prisma.user.createMany({
        data: [
          {
            email: "user1@example.com",
            fullName: "User 1",
            hashedPassword: "password",
          },
          {
            email: "user2@example.com",
            fullName: "User 2",
            hashedPassword: "password",
          },
          {
            email: "user3@example.com",
            fullName: "User 3",
            hashedPassword: "password",
          },
        ],
      });
    });

    it("should return all users with pagination", () => {
      return request(app.getHttpServer())
        .get("/users?page=1&limit=2")
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

    it("should filter users by search term", () => {
      return request(app.getHttpServer())
        .get("/users?search=User 1")
        .expect(200)
        .expect((res) => {
          expect(res.body.data).toHaveLength(1);
          expect(res.body.data[0].fullName).toBe("User 1");
        });
    });
  });

  describe("/users/:id (GET)", () => {
    let userId: string;

    beforeEach(async () => {
      const user = await prisma.user.create({
        data: {
          email: "test@example.com",
          fullName: "Test User",
          hashedPassword: "password",
        },
      });
      userId = user.id;
    });

    it("should return user by id", () => {
      return request(app.getHttpServer())
        .get(`/users/${userId}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.id).toBe(userId);
          expect(res.body.email).toBe("test@example.com");
          expect(res.body.fullName).toBe("Test User");
        });
    });

    it("should return 404 for non-existent user", () => {
      return request(app.getHttpServer())
        .get("/users/non-existent-id")
        .expect(404);
    });
  });

  describe("/users/:id (PUT)", () => {
    let userId: string;

    beforeEach(async () => {
      const user = await prisma.user.create({
        data: {
          email: "test@example.com",
          fullName: "Test User",
          hashedPassword: "password",
        },
      });
      userId = user.id;
    });

    it("should update user", () => {
      const updateUserDto = {
        fullName: "Updated User",
        email: "updated@example.com",
      };

      return request(app.getHttpServer())
        .put(`/users/${userId}`)
        .send(updateUserDto)
        .expect(200)
        .expect((res) => {
          expect(res.body.fullName).toBe(updateUserDto.fullName);
          expect(res.body.email).toBe(updateUserDto.email);
        });
    });

    it("should return 404 for non-existent user", () => {
      return request(app.getHttpServer())
        .put("/users/non-existent-id")
        .send({ fullName: "Updated User" })
        .expect(404);
    });
  });

  describe("/users/:id (DELETE)", () => {
    let userId: string;

    beforeEach(async () => {
      const user = await prisma.user.create({
        data: {
          email: "test@example.com",
          fullName: "Test User",
          hashedPassword: "password",
        },
      });
      userId = user.id;
    });

    it("should delete user", () => {
      return request(app.getHttpServer())
        .delete(`/users/${userId}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.message).toBe("User deleted successfully");
        });
    });

    it("should return 404 for non-existent user", () => {
      return request(app.getHttpServer())
        .delete("/users/non-existent-id")
        .expect(404);
    });
  });
});
