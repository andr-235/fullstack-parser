import { Module } from "@nestjs/common";
import { CacheModule } from "@nestjs/cache-manager";
import { ConfigModule, ConfigService } from "@nestjs/config";
import { RedisService } from "./redis.service";

@Module({
  imports: [
    CacheModule.registerAsync({
      imports: [ConfigModule],
      useFactory: async (configService: ConfigService) => ({
        isGlobal: true,
        store: await import("@keyv/redis").then((m) => m.default),
        url: configService.get("REDIS_URL", "redis://redis:6379/0"),
        ttl: configService.get("REDIS_TTL", 3600), // 1 hour default
        max: configService.get("REDIS_MAX_KEYS", 1000),
        retryDelayOnFailover: 100,
      }),
      inject: [ConfigService],
    }),
  ],
  providers: [RedisService],
  exports: [RedisService, CacheModule],
})
export class RedisModule {}
