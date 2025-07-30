import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service";

@Injectable()
export class MonitoringService {
  constructor(private readonly prisma: PrismaService) {}

  async getMetrics() {
    const startTime = process.hrtime();

    // Basic application metrics
    const metrics = {
      app: {
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        cpu: process.cpuUsage(),
      },
      database: {
        connections: await this.getDatabaseConnections(),
      },
      timestamp: new Date().toISOString(),
    };

    const endTime = process.hrtime(startTime);
    metrics["response_time"] = endTime[0] * 1000 + endTime[1] / 1000000;

    return metrics;
  }

  async getNodeMetrics() {
    return {
      node: {
        version: process.version,
        platform: process.platform,
        arch: process.arch,
        pid: process.pid,
        uptime: process.uptime(),
      },
      memory: {
        ...process.memoryUsage(),
        external: process.memoryUsage().external,
        heapTotal: process.memoryUsage().heapTotal,
        heapUsed: process.memoryUsage().heapUsed,
        rss: process.memoryUsage().rss,
      },
      cpu: process.cpuUsage(),
      timestamp: new Date().toISOString(),
    };
  }

  async getStatus() {
    try {
      // Check database connection
      await this.prisma.$queryRaw`SELECT 1`;

      return {
        status: "healthy",
        services: {
          database: "connected",
          redis: "connected", // You can add Redis check here
        },
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
      };
    } catch (error) {
      return {
        status: "unhealthy",
        error: error.message,
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
      };
    }
  }

  private async getDatabaseConnections() {
    try {
      // This is a simplified version - in production you might want to use
      // a connection pool manager to get actual connection counts
      return {
        active: 1, // Placeholder
        idle: 0, // Placeholder
        total: 1, // Placeholder
      };
    } catch (error) {
      return {
        active: 0,
        idle: 0,
        total: 0,
        error: error.message,
      };
    }
  }
}
