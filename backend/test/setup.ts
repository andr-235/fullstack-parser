import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";
import { PrismaService } from "../src/prisma/prisma.service";
import { AppModule } from "../src/app.module";

export class TestApp {
  private app: INestApplication;
  private prisma: PrismaService;

  async createApp(): Promise<INestApplication> {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    this.app = moduleFixture.createNestApplication();
    this.prisma = this.app.get<PrismaService>(PrismaService);

    await this.app.init();
    return this.app;
  }

  async cleanup(): Promise<void> {
    if (this.prisma) {
      await this.prisma.$disconnect();
    }
    if (this.app) {
      await this.app.close();
    }
  }

  getPrisma(): PrismaService {
    return this.prisma;
  }
}
