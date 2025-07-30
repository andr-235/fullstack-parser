import {
  Controller,
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
import { CommentsService } from "./comments.service";
import { VKCommentResponseDto } from "../../common/dto";

@ApiTags("comments")
@Controller("comments")
export class CommentsController {
  constructor(private readonly commentsService: CommentsService) {}

  @Get()
  @ApiOperation({ summary: "Get all comments with pagination and filtering" })
  @ApiQuery({ name: "page", required: false, description: "Page number" })
  @ApiQuery({ name: "limit", required: false, description: "Items per page" })
  @ApiQuery({
    name: "search",
    required: false,
    description: "Search in comment text",
  })
  @ApiQuery({
    name: "postId",
    required: false,
    description: "Filter by post ID",
  })
  @ApiQuery({
    name: "groupId",
    required: false,
    description: "Filter by group ID",
  })
  @ApiQuery({
    name: "hasKeywords",
    required: false,
    description: "Filter comments with keywords",
  })
  @ApiResponse({
    status: 200,
    description: "Comments retrieved successfully",
    schema: {
      type: "object",
      properties: {
        comments: {
          type: "array",
          items: { $ref: "#/components/schemas/VKCommentResponseDto" },
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
    @Query("postId") postId?: string,
    @Query("groupId") groupId?: string,
    @Query("hasKeywords") hasKeywords?: boolean
  ) {
    const pageNumber = page ? parseInt(page, 10) : 1;
    const limitNumber = limit ? parseInt(limit, 10) : 10;

    if (pageNumber < 1 || limitNumber < 1) {
      throw new BadRequestException("Page and limit must be positive numbers.");
    }

    return this.commentsService.findAll(
      pageNumber,
      limitNumber,
      search,
      postId,
      groupId,
      hasKeywords
    );
  }

  @Get("statistics")
  @ApiOperation({ summary: "Get comment statistics" })
  @ApiResponse({
    status: 200,
    description: "Statistics retrieved successfully",
    schema: {
      type: "object",
      properties: {
        totalComments: { type: "number" },
        commentsWithKeywords: { type: "number" },
        averageCommentsPerPost: { type: "number" },
        topGroups: {
          type: "array",
          items: {
            type: "object",
            properties: {
              groupId: { type: "string" },
              groupName: { type: "string" },
              commentCount: { type: "number" },
            },
          },
        },
      },
    },
  })
  async getStatistics() {
    return this.commentsService.getStatistics();
  }

  @Get("keywords/analysis")
  @ApiOperation({ summary: "Get keyword analysis in comments" })
  @ApiQuery({
    name: "limit",
    required: false,
    description: "Number of top keywords to return",
  })
  @ApiResponse({
    status: 200,
    description: "Keyword analysis retrieved successfully",
    schema: {
      type: "object",
      properties: {
        keywordFrequency: {
          type: "array",
          items: {
            type: "object",
            properties: {
              keyword: { type: "string" },
              count: { type: "number" },
              percentage: { type: "number" },
            },
          },
        },
        totalCommentsWithKeywords: { type: "number" },
        totalComments: { type: "number" },
      },
    },
  })
  async getKeywordAnalysis(@Query("limit") limit?: number) {
    return this.commentsService.getKeywordAnalysis(limit);
  }

  @Get(":id")
  @ApiOperation({ summary: "Get comment by ID" })
  @ApiParam({ name: "id", description: "Comment ID" })
  @ApiResponse({
    status: 200,
    description: "Comment retrieved successfully",
    type: VKCommentResponseDto,
  })
  @ApiResponse({
    status: 404,
    description: "Comment not found",
  })
  async findOne(@Param("id") id: string) {
    return this.commentsService.findOne(id);
  }

  @Get("post/:postId")
  @ApiOperation({ summary: "Get all comments for a specific post" })
  @ApiParam({ name: "postId", description: "Post ID" })
  @ApiQuery({ name: "page", required: false, description: "Page number" })
  @ApiQuery({ name: "limit", required: false, description: "Items per page" })
  @ApiResponse({
    status: 200,
    description: "Comments for post retrieved successfully",
    schema: {
      type: "object",
      properties: {
        comments: {
          type: "array",
          items: { $ref: "#/components/schemas/VKCommentResponseDto" },
        },
        total: { type: "number" },
        page: { type: "number" },
        limit: { type: "number" },
        totalPages: { type: "number" },
      },
    },
  })
  async findByPost(
    @Param("postId") postId: string,
    @Query("page") page?: number,
    @Query("limit") limit?: number
  ) {
    return this.commentsService.findByPost(postId, page, limit);
  }

  @Get("group/:groupId")
  @ApiOperation({ summary: "Get all comments for a specific group" })
  @ApiParam({ name: "groupId", description: "Group ID" })
  @ApiQuery({ name: "page", required: false, description: "Page number" })
  @ApiQuery({ name: "limit", required: false, description: "Items per page" })
  @ApiResponse({
    status: 200,
    description: "Comments for group retrieved successfully",
    schema: {
      type: "object",
      properties: {
        comments: {
          type: "array",
          items: { $ref: "#/components/schemas/VKCommentResponseDto" },
        },
        total: { type: "number" },
        page: { type: "number" },
        limit: { type: "number" },
        totalPages: { type: "number" },
      },
    },
  })
  async findByGroup(
    @Param("groupId") groupId: string,
    @Query("page") page?: number,
    @Query("limit") limit?: number
  ) {
    return this.commentsService.findByGroup(groupId, page, limit);
  }
}
