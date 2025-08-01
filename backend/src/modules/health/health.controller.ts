import { Controller, Get } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse } from "@nestjs/swagger";
import { RedisService } from "../../common/redis";

@ApiTags("health")
@Controller("health")
export class HealthController {
  constructor(private readonly redisService: RedisService) {}

  @Get()
  @ApiOperation({ summary: "Health check endpoint" })
  @ApiResponse({
    status: 200,
    description: "Service is healthy",
    schema: {
      type: "object",
      properties: {
        status: { type: "string", example: "ok" },
        timestamp: { type: "string", example: "2024-01-01T00:00:00.000Z" },
        uptime: { type: "number", example: 123.456 },
        redis: { type: "string", example: "connected" },
      },
    },
  })
  async healthCheck() {
    let redisStatus = "disconnected";
    try {
      await this.redisService.ping();
      redisStatus = "connected";
    } catch (error) {
      console.error("Redis health check failed:", error);
    }

    return {
      status: "ok",
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      redis: redisStatus,
    };
  }
}
