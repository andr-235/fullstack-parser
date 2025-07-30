import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";
import { PrismaModule } from "./prisma/prisma.module";
import { UsersModule } from "./modules/users/users.module";
import { GroupsModule } from "./modules/groups/groups.module";
import { ParserModule } from "./modules/parser/parser.module";
import { KeywordsModule } from "./modules/keywords/keywords.module";
import { CommentsModule } from "./modules/comments/comments.module";

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
    PrismaModule,
    UsersModule,
    GroupsModule,
    ParserModule,
    KeywordsModule,
    CommentsModule,
  ],
})
export class AppModule {}
