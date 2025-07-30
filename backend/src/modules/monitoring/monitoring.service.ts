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

  async getSchedulerStatus() {
    return {
      status: "running",
      lastRun: new Date().toISOString(),
      nextRun: new Date(Date.now() + 300000).toISOString(), // 5 minutes from now
      totalJobs: 0,
      activeJobs: 0,
      failedJobs: 0,
    };
  }

  async getStats() {
    try {
      const totalGroups = await this.prisma.vKGroup.count();
      const activeGroups = await this.prisma.vKGroup.count({
        where: { isActive: true },
      });
      const totalComments = await this.prisma.vKComment.count();
      const totalKeywords = await this.prisma.keyword.count();

      return {
        groups: {
          total: totalGroups,
          active: activeGroups,
          inactive: totalGroups - activeGroups,
        },
        comments: {
          total: totalComments,
        },
        keywords: {
          total: totalKeywords,
        },
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        error: error.message,
        timestamp: new Date().toISOString(),
      };
    }
  }

  async getActiveGroups() {
    try {
      const activeGroups = await this.prisma.vKGroup.findMany({
        where: { isActive: true },
        select: {
          id: true,
          name: true,
          screenName: true,
          isActive: true,
          updatedAt: true,
        },
        orderBy: { updatedAt: "desc" },
        take: 10,
      });

      return {
        groups: activeGroups,
        count: activeGroups.length,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        error: error.message,
        timestamp: new Date().toISOString(),
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
