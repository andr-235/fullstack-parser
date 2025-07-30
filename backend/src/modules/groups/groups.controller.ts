import { Controller, Get, Post, Put, Delete, Body, Param, HttpCode, HttpStatus } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { GroupsService } from './groups.service';
import { VKGroup } from '@prisma/client';

@ApiTags('groups')
@Controller('groups')
export class GroupsController {
  constructor(private readonly groupsService: GroupsService) {}

  @Get()
  @ApiOperation({ summary: 'Get all VK groups' })
  @ApiResponse({ status: 200, description: 'List of VK groups' })
  async findAll(): Promise<VKGroup[]> {
    return this.groupsService.findAll();
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get VK group by ID' })
  @ApiResponse({ status: 200, description: 'VK group found' })
  @ApiResponse({ status: 404, description: 'VK group not found' })
  async findById(@Param('id') id: string): Promise<VKGroup | null> {
    return this.groupsService.findById(id);
  }

  @Get('vk/:vkId')
  @ApiOperation({ summary: 'Get VK group by VK ID' })
  @ApiResponse({ status: 200, description: 'VK group found' })
  @ApiResponse({ status: 404, description: 'VK group not found' })
  async findByVkId(@Param('vkId') vkId: string): Promise<VKGroup | null> {
    return this.groupsService.findByVkId(parseInt(vkId));
  }

  @Post()
  @ApiOperation({ summary: 'Create new VK group' })
  @ApiResponse({ status: 201, description: 'VK group created' })
  @ApiResponse({ status: 400, description: 'Bad request' })
  async create(@Body() data: {
    vkId: number;
    screenName: string;
    name: string;
    description?: string;
  }): Promise<VKGroup> {
    return this.groupsService.create(data);
  }

  @Put(':id')
  @ApiOperation({ summary: 'Update VK group' })
  @ApiResponse({ status: 200, description: 'VK group updated' })
  @ApiResponse({ status: 404, description: 'VK group not found' })
  async update(
    @Param('id') id: string,
    @Body() data: Partial<VKGroup>,
  ): Promise<VKGroup> {
    return this.groupsService.update(id, data);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: 'Delete VK group' })
  @ApiResponse({ status: 204, description: 'VK group deleted' })
  @ApiResponse({ status: 404, description: 'VK group not found' })
  async delete(@Param('id') id: string): Promise<void> {
    await this.groupsService.delete(id);
  }
} 