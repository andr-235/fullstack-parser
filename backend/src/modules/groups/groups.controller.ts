import {
  Controller,
  Get,
  Post,
  Body,
  Patch,
  Param,
  Delete,
  Query,
  HttpCode,
  HttpStatus,
  BadRequestException,
} from "@nestjs/common";
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiParam,
  ApiQuery,
} from "@nestjs/swagger";
import { GroupsService } from "./groups.service";
import {
  CreateVKGroupDto,
  UpdateVKGroupDto,
  VKGroupResponseDto,
} from "../../common/dto";

@ApiTags("groups")
@Controller("groups")
export class GroupsController {
  constructor(private readonly groupsService: GroupsService) {}

  @Post()
  @ApiOperation({ summary: "Create a new VK group" })
  @ApiResponse({
    status: 201,
    description: "Group created successfully",
    type: VKGroupResponseDto,
  })
  @ApiResponse({
    status: 409,
    description: "Group with this VK ID or screen name already exists",
  })
  async create(
    @Body() createGroupDto: CreateVKGroupDto
  ): Promise<VKGroupResponseDto> {
    return this.groupsService.create(createGroupDto);
  }

  @Get()
  @ApiOperation({ summary: "Get all groups with pagination and filtering" })
  @ApiQuery({ name: "page", required: false, description: "Page number" })
  @ApiQuery({ name: "limit", required: false, description: "Items per page" })
  @ApiQuery({
    name: "search",
    required: false,
    description: "Search in group name, screen name, or description",
  })
  @ApiQuery({
    name: "isActive",
    required: false,
    description: "Filter by active status",
  })
  @ApiResponse({
    status: 200,
    description: "Groups retrieved successfully",
    schema: {
      type: "object",
      properties: {
        groups: {
          type: "array",
          items: { $ref: "#/components/schemas/VKGroupResponseDto" },
        },
        total: { type: "number" },
        page: { type: "number" },
        limit: { type: "number" },
        totalPages: { type: "number" },
      },
    },
  })
  async findAll(
    @Query("page") page?: string,
    @Query("limit") limit?: string,
    @Query("search") search?: string,
    @Query("isActive") isActive?: boolean
  ) {
    // Конвертация и валидация параметров
    const pageNum = page ? parseInt(page, 10) : 1;
    const limitNum = limit ? parseInt(limit, 10) : 20;

    // Проверка валидности
    if (isNaN(pageNum) || pageNum < 1) {
      throw new BadRequestException("Page must be a positive number");
    }
    if (isNaN(limitNum) || limitNum < 1 || limitNum > 100) {
      throw new BadRequestException("Limit must be between 1 and 100");
    }

    return this.groupsService.findAll(pageNum, limitNum, search, isActive);
  }

  @Get("all")
  @ApiOperation({ summary: "Get all groups without pagination" })
  @ApiResponse({
    status: 200,
    description: "All groups retrieved successfully",
    type: [VKGroupResponseDto],
  })
  async findAllWithoutPagination(): Promise<VKGroupResponseDto[]> {
    const result = await this.groupsService.findAll(1, 10000); // Большой лимит для получения всех
    return result.groups;
  }

  @Get("statistics")
  @ApiOperation({ summary: "Get group statistics" })
  @ApiResponse({
    status: 200,
    description: "Statistics retrieved successfully",
    schema: {
      type: "object",
      properties: {
        totalGroups: { type: "number" },
        activeGroups: { type: "number" },
        inactiveGroups: { type: "number" },
        groupsWithPosts: { type: "number" },
        averagePostsPerGroup: { type: "number" },
        topGroups: {
          type: "array",
          items: {
            type: "object",
            properties: {
              id: { type: "string" },
              vkId: { type: "number" },
              screenName: { type: "string" },
              name: { type: "string" },
              postCount: { type: "number" },
            },
          },
        },
      },
    },
  })
  async getStatistics() {
    return this.groupsService.getStatistics();
  }

  @Get("search")
  @ApiOperation({
    summary: "Search groups by name, screen name, or description",
  })
  @ApiQuery({ name: "q", required: true, description: "Search query" })
  @ApiQuery({
    name: "limit",
    required: false,
    description: "Number of results to return",
  })
  @ApiResponse({
    status: 200,
    description: "Search results retrieved successfully",
    type: [VKGroupResponseDto],
  })
  async searchGroups(
    @Query("q") query: string,
    @Query("limit") limit?: number
  ) {
    return this.groupsService.searchGroups(query, limit);
  }

  @Get("by-post-count")
  @ApiOperation({ summary: "Get groups filtered by minimum post count" })
  @ApiQuery({
    name: "minPosts",
    required: false,
    description: "Minimum number of posts",
  })
  @ApiResponse({
    status: 200,
    description: "Groups filtered by post count retrieved successfully",
    type: [VKGroupResponseDto],
  })
  async getGroupsByPostCount(@Query("minPosts") minPosts?: number) {
    return this.groupsService.getGroupsByPostCount(minPosts);
  }

  @Get(":id")
  @ApiOperation({ summary: "Get group by ID" })
  @ApiParam({ name: "id", description: "Group ID" })
  @ApiResponse({
    status: 200,
    description: "Group retrieved successfully",
    type: VKGroupResponseDto,
  })
  @ApiResponse({
    status: 404,
    description: "Group not found",
  })
  async findOne(@Param("id") id: string): Promise<VKGroupResponseDto> {
    return this.groupsService.findOne(id);
  }

  @Get("vk/:vkId")
  @ApiOperation({ summary: "Get group by VK ID" })
  @ApiParam({ name: "vkId", description: "VK Group ID" })
  @ApiResponse({
    status: 200,
    description: "Group retrieved successfully",
    type: VKGroupResponseDto,
  })
  @ApiResponse({
    status: 404,
    description: "Group not found",
  })
  async findByVkId(@Param("vkId") vkId: number): Promise<VKGroupResponseDto> {
    return this.groupsService.findByVkId(vkId);
  }

  @Get("screen/:screenName")
  @ApiOperation({ summary: "Get group by screen name" })
  @ApiParam({ name: "screenName", description: "VK Group screen name" })
  @ApiResponse({
    status: 200,
    description: "Group retrieved successfully",
    type: VKGroupResponseDto,
  })
  @ApiResponse({
    status: 404,
    description: "Group not found",
  })
  async findByScreenName(
    @Param("screenName") screenName: string
  ): Promise<VKGroupResponseDto> {
    return this.groupsService.findByScreenName(screenName);
  }

  @Patch(":id")
  @ApiOperation({ summary: "Update group" })
  @ApiParam({ name: "id", description: "Group ID" })
  @ApiResponse({
    status: 200,
    description: "Group updated successfully",
    type: VKGroupResponseDto,
  })
  @ApiResponse({
    status: 404,
    description: "Group not found",
  })
  async update(
    @Param("id") id: string,
    @Body() updateGroupDto: UpdateVKGroupDto
  ): Promise<VKGroupResponseDto> {
    return this.groupsService.update(id, updateGroupDto);
  }

  @Patch("bulk/status")
  @ApiOperation({ summary: "Bulk update group status" })
  @ApiResponse({
    status: 200,
    description: "Groups updated successfully",
    schema: {
      type: "object",
      properties: {
        updatedCount: { type: "number" },
      },
    },
  })
  async bulkUpdateStatus(@Body() data: { ids: string[]; isActive: boolean }) {
    const updatedCount = await this.groupsService.bulkUpdateStatus(
      data.ids,
      data.isActive
    );
    return { updatedCount };
  }

  @Delete(":id")
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: "Delete group" })
  @ApiParam({ name: "id", description: "Group ID" })
  @ApiResponse({
    status: 204,
    description: "Group deleted successfully",
  })
  @ApiResponse({
    status: 404,
    description: "Group not found",
  })
  async remove(@Param("id") id: string): Promise<void> {
    await this.groupsService.remove(id);
  }
}
