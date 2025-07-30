import {
  Controller,
  Get,
  Post,
  Body,
  Patch,
  Param,
  Delete,
  HttpCode,
  HttpStatus,
  Query,
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
  @ApiOperation({ summary: "Get all VK groups" })
  @ApiResponse({
    status: 200,
    description: "List of all groups",
    type: [VKGroupResponseDto],
  })
  async findAll(): Promise<VKGroupResponseDto[]> {
    return this.groupsService.findAll();
  }

  @Get("search")
  @ApiOperation({ summary: "Search groups by VK ID or screen name" })
  @ApiQuery({ name: "vkId", description: "VK Group ID", required: false })
  @ApiQuery({
    name: "screenName",
    description: "VK Group screen name",
    required: false,
  })
  @ApiResponse({
    status: 200,
    description: "Group found",
    type: VKGroupResponseDto,
  })
  async search(
    @Query("vkId") vkId?: string,
    @Query("screenName") screenName?: string
  ): Promise<VKGroupResponseDto | null> {
    if (vkId) {
      return this.groupsService.findByVkId(parseInt(vkId));
    }
    if (screenName) {
      return this.groupsService.findByScreenName(screenName);
    }
    return null;
  }

  @Get(":id")
  @ApiOperation({ summary: "Get group by ID" })
  @ApiParam({ name: "id", description: "Group ID" })
  @ApiResponse({
    status: 200,
    description: "Group found",
    type: VKGroupResponseDto,
  })
  @ApiResponse({
    status: 404,
    description: "Group not found",
  })
  async findOne(@Param("id") id: string): Promise<VKGroupResponseDto> {
    return this.groupsService.findOne(id);
  }

  @Patch(":id")
  @ApiOperation({ summary: "Update group by ID" })
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

  @Delete(":id")
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: "Delete group by ID" })
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
    return this.groupsService.remove(id);
  }
}
