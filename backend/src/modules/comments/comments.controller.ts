import { Controller, Get, Post, Put, Delete, Body, Param, Query, HttpCode, HttpStatus } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery } from '@nestjs/swagger';
import { CommentsService } from './comments.service';
import { VKComment } from '@prisma/client';

@ApiTags('comments')
@Controller('comments')
export class CommentsController {
  constructor(private readonly commentsService: CommentsService) {}

  @Get()
  @ApiOperation({ summary: 'Get all comments' })
  @ApiResponse({ status: 200, description: 'List of comments' })
  async findAll(): Promise<VKComment[]> {
    return this.commentsService.findAll();
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get comment by ID' })
  @ApiResponse({ status: 200, description: 'Comment found' })
  @ApiResponse({ status: 404, description: 'Comment not found' })
  async findById(@Param('id') id: string): Promise<VKComment | null> {
    return this.commentsService.findById(id);
  }

  @Get('post/:postId')
  @ApiOperation({ summary: 'Get comments by post ID' })
  @ApiResponse({ status: 200, description: 'Comments found' })
  async findByPostId(@Param('postId') postId: string): Promise<VKComment[]> {
    return this.commentsService.findByPostId(postId);
  }

  @Get('search/text')
  @ApiOperation({ summary: 'Search comments by text' })
  @ApiQuery({ name: 'q', description: 'Search query' })
  @ApiResponse({ status: 200, description: 'Comments found' })
  async searchByText(@Query('q') query: string): Promise<VKComment[]> {
    return this.commentsService.searchByText(query);
  }

  @Post()
  @ApiOperation({ summary: 'Create new comment' })
  @ApiResponse({ status: 201, description: 'Comment created' })
  @ApiResponse({ status: 400, description: 'Bad request' })
  async create(@Body() data: {
    vkId: number;
    postId: string;
    text: string;
  }): Promise<VKComment> {
    return this.commentsService.create(data);
  }

  @Put(':id')
  @ApiOperation({ summary: 'Update comment' })
  @ApiResponse({ status: 200, description: 'Comment updated' })
  @ApiResponse({ status: 404, description: 'Comment not found' })
  async update(
    @Param('id') id: string,
    @Body() data: Partial<VKComment>,
  ): Promise<VKComment> {
    return this.commentsService.update(id, data);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: 'Delete comment' })
  @ApiResponse({ status: 204, description: 'Comment deleted' })
  @ApiResponse({ status: 404, description: 'Comment not found' })
  async delete(@Param('id') id: string): Promise<void> {
    await this.commentsService.delete(id);
  }
} 