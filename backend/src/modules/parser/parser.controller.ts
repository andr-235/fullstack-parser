import {
  Controller,
  Post,
  Get,
  Param,
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
import { ParserService } from "./parser.service";
import { VKGroup, VKPost, VKComment } from "@prisma/client";

@ApiTags("parser")
@Controller("parser")
export class ParserController {
  constructor(private readonly parserService: ParserService) {}

  @Post("groups/:screenName")
  @ApiOperation({ summary: "Parse VK group by screen name" })
  @ApiParam({ name: "screenName", description: "VK group screen name" })
  @ApiResponse({
    status: 201,
    description: "Group parsed successfully",
    type: VKGroup,
  })
  @ApiResponse({
    status: 400,
    description: "Invalid screen name",
  })
  @ApiResponse({
    status: 404,
    description: "Group not found",
  })
  async parseGroup(@Param("screenName") screenName: string): Promise<VKGroup> {
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
    type: [VKPost],
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
  ): Promise<VKPost[]> {
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
    type: [VKComment],
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
  ): Promise<VKComment[]> {
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
    group: VKGroup;
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
    group: VKGroup;
    postsParsed: number;
    commentsParsed: number;
    keywordsMatched: number;
  }> {
    // Parse group if not exists
    const group = await this.parserService.parseGroup(groupId);

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
}
