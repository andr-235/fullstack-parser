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
      // Очищаем базу данных в правильном порядке (от зависимых к независимым)
      await this.prisma.commentKeywordMatch.deleteMany();
      await this.prisma.vKComment.deleteMany();
      await this.prisma.vKPost.deleteMany();
      await this.prisma.vKGroup.deleteMany();
      await this.prisma.keyword.deleteMany();
      await this.prisma.user.deleteMany();
      
      await this.prisma.$disconnect();
    }
    if (this.app) {
      await this.app.close();
    }
  }

  async resetDatabase(): Promise<void> {
    if (this.prisma) {
      // Очищаем базу данных в правильном порядке
      await this.prisma.commentKeywordMatch.deleteMany();
      await this.prisma.vKComment.deleteMany();
      await this.prisma.vKPost.deleteMany();
      await this.prisma.vKGroup.deleteMany();
      await this.prisma.keyword.deleteMany();
      await this.prisma.user.deleteMany();
    }
  }

  getPrisma(): PrismaService {
    return this.prisma;
  }
}
