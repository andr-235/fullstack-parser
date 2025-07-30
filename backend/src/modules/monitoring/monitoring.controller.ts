import { Controller, Get } from "@nestjs/common";
import { MonitoringService } from "./monitoring.service";
import { ApiTags, ApiOperation, ApiResponse } from "@nestjs/swagger";

@ApiTags("Monitoring")
@Controller("monitoring")
export class MonitoringController {
  constructor(private readonly monitoringService: MonitoringService) {}

  @Get("metrics")
  @ApiOperation({ summary: "Prometheus metrics endpoint" })
  @ApiResponse({ status: 200, description: "Application metrics" })
  async getMetrics() {
    return this.monitoringService.getMetrics();
  }

  @Get("node-metrics")
  @ApiOperation({ summary: "Node.js specific metrics" })
  @ApiResponse({ status: 200, description: "Node.js metrics" })
  async getNodeMetrics() {
    return this.monitoringService.getNodeMetrics();
  }

  @Get("status")
  @ApiOperation({ summary: "Application status" })
  @ApiResponse({ status: 200, description: "Application status information" })
  async getStatus() {
    return this.monitoringService.getStatus();
  }

  @Get("scheduler/status")
  @ApiOperation({ summary: "Scheduler status" })
  @ApiResponse({ status: 200, description: "Scheduler status information" })
  async getSchedulerStatus() {
    return this.monitoringService.getSchedulerStatus();
  }

  @Get("stats")
  @ApiOperation({ summary: "Monitoring statistics" })
  @ApiResponse({ status: 200, description: "Monitoring statistics" })
  async getStats() {
    return this.monitoringService.getStats();
  }

  @Get("groups/active")
  @ApiOperation({ summary: "Active groups monitoring" })
  @ApiResponse({ status: 200, description: "Active groups information" })
  async getActiveGroups() {
    return this.monitoringService.getActiveGroups();
  }
}
