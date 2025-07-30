import { Controller, Post, Get, Param, Query, HttpCode, HttpStatus } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiParam, ApiQuery } from '@nestjs/swagger';
import { ParserService } from './parser.service';
import { VKGroup, VKPost, VKComment } from '@prisma/client';

@ApiTags('parser')
@Controller('parser')
export class ParserController {
  constructor(private readonly parserService: ParserService) {}

  @Post('groups/:screenName')
  @ApiOperation({ summary: 'Parse VK group by screen name' })
  @ApiParam({ name: 'screenName', description: 'VK group screen name' })
  @ApiResponse({ status: 201, description: 'Group parsed successfully' })
  @ApiResponse({ status: 400, description: 'Bad request' })
  @ApiResponse({ status: 404, description: 'Group not found' })
  async parseGroup(@Param('screenName') screenName: string): Promise<VKGroup> {
    return this.parserService.parseGroup(screenName);
  }

  @Post('groups/:groupId/posts')
  @ApiOperation({ summary: 'Parse posts for a VK group' })
  @ApiParam({ name: 'groupId', description: 'Database group ID' })
  @ApiQuery({ name: 'limit', required: false, description: 'Number of posts to parse', type: Number })
  @ApiResponse({ status: 201, description: 'Posts parsed successfully' })
  @ApiResponse({ status: 400, description: 'Bad request' })
  @ApiResponse({ status: 404, description: 'Group not found' })
  async parseGroupPosts(
    @Param('groupId') groupId: string,
    @Query('limit') limit: number = 100,
  ): Promise<VKPost[]> {
    return this.parserService.parseGroupPosts(groupId, limit);
  }

  @Post('posts/:postId/comments')
  @ApiOperation({ summary: 'Parse comments for a VK post' })
  @ApiParam({ name: 'postId', description: 'Database post ID' })
  @ApiQuery({ name: 'limit', required: false, description: 'Number of comments to parse', type: Number })
  @ApiResponse({ status: 201, description: 'Comments parsed successfully' })
  @ApiResponse({ status: 400, description: 'Bad request' })
  @ApiResponse({ status: 404, description: 'Post not found' })
  async parsePostComments(
    @Param('postId') postId: string,
    @Query('limit') limit: number = 100,
  ): Promise<VKComment[]> {
    return this.parserService.parsePostComments(postId, limit);
  }

  @Post('groups/:groupId/full')
  @ApiOperation({ summary: 'Parse full group data (group, posts, and comments)' })
  @ApiParam({ name: 'groupId', description: 'Database group ID' })
  @ApiQuery({ name: 'postsLimit', required: false, description: 'Number of posts to parse', type: Number })
  @ApiQuery({ name: 'commentsLimit', required: false, description: 'Number of comments per post', type: Number })
  @ApiResponse({ status: 201, description: 'Full group data parsed successfully' })
  @ApiResponse({ status: 400, description: 'Bad request' })
  @ApiResponse({ status: 404, description: 'Group not found' })
  async parseFullGroup(
    @Param('groupId') groupId: string,
    @Query('postsLimit') postsLimit: number = 100,
    @Query('commentsLimit') commentsLimit: number = 100,
  ): Promise<{
    group: VKGroup;
    posts: VKPost[];
    totalComments: number;
  }> {
    const group = await this.parserService.parseGroup(groupId);
    const posts = await this.parserService.parseGroupPosts(groupId, postsLimit);
    
    let totalComments = 0;
    for (const post of posts) {
      const comments = await this.parserService.parsePostComments(post.id, commentsLimit);
      totalComments += comments.length;
    }

    return {
      group,
      posts,
      totalComments,
    };
  }
} 