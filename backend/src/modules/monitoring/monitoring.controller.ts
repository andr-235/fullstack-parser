import { Controller, Get } from "@nestjs/common";
import { MonitoringService } from "./monitoring.service";
import { ApiTags, ApiOperation, ApiResponse } from "@nestjs/swagger";

@ApiTags("Monitoring")
@Controller("api")
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
}
