import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";
import { PrismaModule } from "./prisma/prisma.module";
import { UsersModule } from "./modules/users/users.module";
import { GroupsModule } from "./modules/groups/groups.module";
import { ParserModule } from "./modules/parser/parser.module";
import { KeywordsModule } from "./modules/keywords/keywords.module";
import { CommentsModule } from "./modules/comments/comments.module";
import { HealthModule } from "./modules/health/health.module";
import { MonitoringModule } from "./modules/monitoring/monitoring.module";
import { RedisModule } from "./common/redis";

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: [
        ".env",
        ".env.local",
        ".env.development",
        ".env.production",
      ],
    }),
    RedisModule,
    PrismaModule,
    UsersModule,
    GroupsModule,
    ParserModule,
    KeywordsModule,
    CommentsModule,
    HealthModule,
    MonitoringModule,
  ],
})
export class AppModule {}
