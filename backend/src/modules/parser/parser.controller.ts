import {
  Controller,
  Post,
  Get,
  Delete,
  Param,
  Query,
  Body,
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
import { ParserService } from "./parser.service";
import { VkApiService } from "./vk-api.service";
import { VKGroupDto, VKPostDto, VKCommentDto } from "../../common/dto/vk.dto";
import {
  ParseTaskCreate,
  ParseTaskResponse,
  ParseTaskStatus,
} from "../../common/dto/parser.dto";

@ApiTags("parser")
@Controller("parser")
export class ParserController {
  constructor(
    private readonly parserService: ParserService,
    private readonly vkApiService: VkApiService
  ) {}

  @Post("groups/:screenName")
  @ApiOperation({ summary: "Parse VK group by screen name" })
  @ApiParam({ name: "screenName", description: "VK group screen name" })
  @ApiResponse({
    status: 201,
    description: "Group parsed successfully",
    type: VKGroupDto,
  })
  @ApiResponse({
    status: 400,
    description: "Invalid screen name",
  })
  @ApiResponse({
    status: 404,
    description: "Group not found",
  })
  async parseGroup(
    @Param("screenName") screenName: string
  ): Promise<VKGroupDto> {
    return this.parserService.parseGroup(screenName);
  }

  @Post("groups/:groupId/posts")
  @ApiOperation({ summary: "Parse posts for a VK group" })
  @ApiParam({ name: "groupId", description: "Group ID" })
  @ApiQuery({
    name: "limit",
    required: false,
    description: "Number of posts to parse (1-1000)",
    type: Number,
  })
  @ApiResponse({
    status: 201,
    description: "Posts parsed successfully",
    type: [VKPostDto],
  })
  @ApiResponse({
    status: 400,
    description: "Invalid limit parameter",
  })
  @ApiResponse({
    status: 404,
    description: "Group not found",
  })
  async parseGroupPosts(
    @Param("groupId") groupId: string,
    @Query("limit") limit: number = 100
  ): Promise<VKPostDto[]> {
    return this.parserService.parseGroupPosts(groupId, limit);
  }

  @Post("posts/:postId/comments")
  @ApiOperation({ summary: "Parse comments for a VK post" })
  @ApiParam({ name: "postId", description: "Post ID" })
  @ApiQuery({
    name: "limit",
    required: false,
    description: "Number of comments to parse (1-1000)",
    type: Number,
  })
  @ApiResponse({
    status: 201,
    description: "Comments parsed successfully",
    type: [VKCommentDto],
  })
  @ApiResponse({
    status: 400,
    description: "Invalid limit parameter",
  })
  @ApiResponse({
    status: 404,
    description: "Post not found",
  })
  async parsePostComments(
    @Param("postId") postId: string,
    @Query("limit") limit: number = 100
  ): Promise<VKCommentDto[]> {
    return this.parserService.parsePostComments(postId, limit);
  }

  @Post("comments/:commentId/keywords")
  @ApiOperation({ summary: "Match keywords for a specific comment" })
  @ApiParam({ name: "commentId", description: "Comment ID" })
  @ApiResponse({
    status: 200,
    description: "Keywords matched successfully",
  })
  @ApiResponse({
    status: 404,
    description: "Comment not found",
  })
  @HttpCode(HttpStatus.OK)
  async matchKeywordsForComment(
    @Param("commentId") commentId: string
  ): Promise<{ message: string }> {
    await this.parserService.matchKeywordsForComment(commentId);
    return { message: "Keywords matched successfully" };
  }

  @Post("comments/keywords/batch")
  @ApiOperation({ summary: "Match keywords for all comments without matches" })
  @ApiResponse({
    status: 200,
    description: "Batch keyword matching completed",
  })
  @HttpCode(HttpStatus.OK)
  async matchKeywordsForAllComments(): Promise<{ message: string }> {
    await this.parserService.matchKeywordsForAllComments();
    return { message: "Batch keyword matching completed" };
  }

  @Get("stats")
  @ApiOperation({ summary: "Get parsing statistics" })
  @ApiResponse({
    status: 200,
    description: "Parsing statistics",
    schema: {
      type: "object",
      properties: {
        totalGroups: { type: "number" },
        totalPosts: { type: "number" },
        totalComments: { type: "number" },
        totalKeywords: { type: "number" },
        totalMatches: { type: "number" },
      },
    },
  })
  async getParsingStats(): Promise<{
    totalGroups: number;
    totalPosts: number;
    totalComments: number;
    totalKeywords: number;
    totalMatches: number;
  }> {
    return this.parserService.getParsingStats();
  }

  @Get("groups/:groupId/stats")
  @ApiOperation({ summary: "Get statistics for a specific group" })
  @ApiParam({ name: "groupId", description: "Group ID" })
  @ApiResponse({
    status: 200,
    description: "Group statistics",
    schema: {
      type: "object",
      properties: {
        group: { type: "object" },
        postsCount: { type: "number" },
        commentsCount: { type: "number" },
        matchesCount: { type: "number" },
      },
    },
  })
  @ApiResponse({
    status: 404,
    description: "Group not found",
  })
  async getGroupStats(@Param("groupId") groupId: string): Promise<{
    group: VKGroupDto;
    postsCount: number;
    commentsCount: number;
    matchesCount: number;
  }> {
    return this.parserService.getGroupStats(groupId);
  }

  @Post("groups/:groupId/full-parse")
  @ApiOperation({
    summary: "Perform full parsing for a group (posts + comments + keywords)",
  })
  @ApiParam({ name: "groupId", description: "Group ID" })
  @ApiQuery({
    name: "postsLimit",
    required: false,
    description: "Number of posts to parse",
    type: Number,
  })
  @ApiQuery({
    name: "commentsLimit",
    required: false,
    description: "Number of comments per post",
    type: Number,
  })
  @ApiResponse({
    status: 201,
    description: "Full parsing completed",
    schema: {
      type: "object",
      properties: {
        group: { type: "object" },
        postsParsed: { type: "number" },
        commentsParsed: { type: "number" },
        keywordsMatched: { type: "number" },
      },
    },
  })
  async fullParseGroup(
    @Param("groupId") groupId: string,
    @Query("postsLimit") postsLimit: number = 100,
    @Query("commentsLimit") commentsLimit: number = 100
  ): Promise<{
    group: VKGroupDto;
    postsParsed: number;
    commentsParsed: number;
    keywordsMatched: number;
  }> {
    // Get existing group by ID
    const group = await this.parserService.getGroupById(groupId);

    // Parse posts
    const posts = await this.parserService.parseGroupPosts(
      group.id,
      postsLimit
    );

    // Parse comments for each post
    let totalComments = 0;
    for (const post of posts) {
      const comments = await this.parserService.parsePostComments(
        post.id,
        commentsLimit
      );
      totalComments += comments.length;
    }

    // Match keywords for all comments
    await this.parserService.matchKeywordsForAllComments();

    // Get final stats
    const stats = await this.parserService.getGroupStats(group.id);

    return {
      group,
      postsParsed: posts.length,
      commentsParsed: totalComments,
      keywordsMatched: stats.matchesCount,
    };
  }

  @Get("vk/user/:userId")
  @ApiOperation({ summary: "Get VK user information" })
  @ApiParam({ name: "userId", description: "VK user ID or screen name" })
  @ApiResponse({
    status: 200,
    description: "User information retrieved successfully",
  })
  @ApiResponse({
    status: 404,
    description: "User not found",
  })
  async getVkUser(@Param("userId") userId: string) {
    return this.vkApiService.getUser(userId);
  }

  @Get("vk/group/:groupId")
  @ApiOperation({ summary: "Get VK group information" })
  @ApiParam({ name: "groupId", description: "VK group ID or screen name" })
  @ApiResponse({
    status: 200,
    description: "Group information retrieved successfully",
  })
  @ApiResponse({
    status: 404,
    description: "Group not found",
  })
  async getVkGroup(@Param("groupId") groupId: string) {
    return this.vkApiService.getGroup(groupId);
  }

  @Get("vk/wall/:ownerId")
  @ApiOperation({ summary: "Get VK wall posts" })
  @ApiParam({ name: "ownerId", description: "Owner ID (user or group)" })
  @ApiQuery({
    name: "count",
    required: false,
    description: "Number of posts to get",
    type: Number,
  })
  @ApiQuery({
    name: "offset",
    required: false,
    description: "Offset for pagination",
    type: Number,
  })
  @ApiResponse({
    status: 200,
    description: "Wall posts retrieved successfully",
  })
  async getVkWallPosts(
    @Param("ownerId") ownerId: number,
    @Query("count") count: number = 100,
    @Query("offset") offset: number = 0
  ) {
    return this.vkApiService.getWallPosts(ownerId, count, offset);
  }

  @Get("vk/search")
  @ApiOperation({ summary: "Search VK posts" })
  @ApiQuery({
    name: "query",
    required: true,
    description: "Search query",
  })
  @ApiQuery({
    name: "ownerId",
    required: false,
    description: "Owner ID to search in",
    type: Number,
  })
  @ApiQuery({
    name: "count",
    required: false,
    description: "Number of posts to get",
    type: Number,
  })
  @ApiResponse({
    status: 200,
    description: "Search results retrieved successfully",
  })
  async searchVkPosts(
    @Query("query") query: string,
    @Query("ownerId") ownerId?: number,
    @Query("count") count: number = 100
  ) {
    return this.vkApiService.searchPosts(query, ownerId, count);
  }

  @Get("vk/token/check")
  @ApiOperation({ summary: "Check VK token validity" })
  @ApiResponse({
    status: 200,
    description: "Token check result",
    schema: {
      type: "object",
      properties: {
        valid: { type: "boolean" },
      },
    },
  })
  async checkVkToken() {
    const valid = await this.vkApiService.checkToken();
    return { valid };
  }

  @Post("tasks")
  @ApiOperation({ summary: "Create parsing task for multiple groups" })
  @ApiResponse({
    status: 201,
    description: "Task created successfully",
    type: ParseTaskResponse,
  })
  async createParseTask(
    @Body() taskData: ParseTaskCreate
  ): Promise<ParseTaskResponse> {
    return this.parserService.createParseTask(taskData);
  }

  @Get("tasks/:taskId")
  @ApiOperation({ summary: "Get parsing task status" })
  @ApiParam({ name: "taskId", description: "Task ID" })
  @ApiResponse({
    status: 200,
    description: "Task status retrieved successfully",
    type: ParseTaskStatus,
  })
  async getParseTaskStatus(
    @Param("taskId") taskId: string
  ): Promise<ParseTaskStatus> {
    return this.parserService.getParseTaskStatus(taskId);
  }

  @Get("tasks")
  @ApiOperation({ summary: "Get all parsing tasks" })
  @ApiResponse({
    status: 200,
    description: "Tasks list retrieved successfully",
    type: [ParseTaskResponse],
  })
  async getAllParseTasks(): Promise<ParseTaskResponse[]> {
    return this.parserService.getAllParseTasks();
  }

  @Delete("tasks/:taskId")
  @ApiOperation({ summary: "Cancel parsing task" })
  @ApiParam({ name: "taskId", description: "Task ID" })
  @ApiResponse({
    status: 200,
    description: "Task cancelled successfully",
  })
  async cancelParseTask(
    @Param("taskId") taskId: string
  ): Promise<{ message: string }> {
    return this.parserService.cancelParseTask(taskId);
  }
}
