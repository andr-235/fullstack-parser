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
} from "@nestjs/common";
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiParam,
  ApiQuery,
} from "@nestjs/swagger";
import { KeywordsService } from "./keywords.service";
import {
  CreateKeywordDto,
  UpdateKeywordDto,
  KeywordResponseDto,
} from "../../common/dto";

@ApiTags("keywords")
@Controller("keywords")
export class KeywordsController {
  constructor(private readonly keywordsService: KeywordsService) {}

  @Post()
  @ApiOperation({ summary: "Create a new keyword" })
  @ApiResponse({
    status: 201,
    description: "Keyword created successfully",
    type: KeywordResponseDto,
  })
  @ApiResponse({
    status: 409,
    description: "Keyword already exists",
  })
  async create(
    @Body() createKeywordDto: CreateKeywordDto
  ): Promise<KeywordResponseDto> {
    return this.keywordsService.create(createKeywordDto);
  }

  @Post("bulk")
  @ApiOperation({ summary: "Create multiple keywords in bulk" })
  @ApiResponse({
    status: 201,
    description: "Keywords created successfully",
    type: [KeywordResponseDto],
  })
  @ApiResponse({
    status: 400,
    description: "Invalid keywords array",
  })
  async bulkCreate(@Body() keywords: string[]): Promise<KeywordResponseDto[]> {
    return this.keywordsService.bulkCreate(keywords);
  }

  @Get()
  @ApiOperation({ summary: "Get all keywords with pagination and filtering" })
  @ApiQuery({
    name: "page",
    required: false,
    description: "Page number",
    type: Number,
  })
  @ApiQuery({
    name: "limit",
    required: false,
    description: "Items per page",
    type: Number,
  })
  @ApiQuery({ name: "search", required: false, description: "Search term" })
  @ApiQuery({
    name: "isActive",
    required: false,
    description: "Filter by active status",
    type: Boolean,
  })
  @ApiResponse({
    status: 200,
    description: "List of keywords with pagination info",
    schema: {
      type: "object",
      properties: {
        keywords: {
          type: "array",
          items: { $ref: "#/components/schemas/KeywordResponseDto" },
        },
        total: { type: "number" },
        page: { type: "number" },
        limit: { type: "number" },
        totalPages: { type: "number" },
      },
    },
  })
  async findAll(
    @Query("page") page: number = 1,
    @Query("limit") limit: number = 20,
    @Query("search") search?: string,
    @Query("isActive") isActive?: boolean
  ) {
    return this.keywordsService.findAll(page, limit, search, isActive);
  }

  @Get("search")
  @ApiOperation({ summary: "Search keywords" })
  @ApiQuery({ name: "query", required: true, description: "Search query" })
  @ApiQuery({
    name: "limit",
    required: false,
    description: "Maximum results",
    type: Number,
  })
  @ApiResponse({
    status: 200,
    description: "Search results",
    type: [KeywordResponseDto],
  })
  @ApiResponse({
    status: 400,
    description: "Invalid search query",
  })
  async searchKeywords(
    @Query("query") query: string,
    @Query("limit") limit: number = 20
  ): Promise<KeywordResponseDto[]> {
    return this.keywordsService.searchKeywords(query, limit);
  }

  @Get("top")
  @ApiOperation({ summary: "Get top keywords by match count" })
  @ApiQuery({
    name: "limit",
    required: false,
    description: "Number of top keywords",
    type: Number,
  })
  @ApiResponse({
    status: 200,
    description: "Top keywords with match counts",
    schema: {
      type: "array",
      items: {
        type: "object",
        properties: {
          keyword: { $ref: "#/components/schemas/KeywordResponseDto" },
          matchesCount: { type: "number" },
        },
      },
    },
  })
  async getTopKeywords(@Query("limit") limit: number = 10) {
    return this.keywordsService.getTopKeywords(limit);
  }

  @Get("stats")
  @ApiOperation({ summary: "Get keyword statistics" })
  @ApiResponse({
    status: 200,
    description: "Keyword statistics",
    schema: {
      type: "object",
      properties: {
        totalKeywords: { type: "number" },
        activeKeywords: { type: "number" },
        inactiveKeywords: { type: "number" },
        totalMatches: { type: "number" },
        averageMatchesPerKeyword: { type: "number" },
      },
    },
  })
  async getKeywordStats() {
    return this.keywordsService.getKeywordStats();
  }

  @Get(":id")
  @ApiOperation({ summary: "Get keyword by ID" })
  @ApiParam({ name: "id", description: "Keyword ID" })
  @ApiResponse({
    status: 200,
    description: "Keyword found",
    type: KeywordResponseDto,
  })
  @ApiResponse({
    status: 404,
    description: "Keyword not found",
  })
  async findOne(@Param("id") id: string): Promise<KeywordResponseDto> {
    return this.keywordsService.findOne(id);
  }

  @Get("word/:word")
  @ApiOperation({ summary: "Get keyword by word" })
  @ApiParam({ name: "word", description: "Keyword word" })
  @ApiResponse({
    status: 200,
    description: "Keyword found",
    type: KeywordResponseDto,
  })
  @ApiResponse({
    status: 404,
    description: "Keyword not found",
  })
  async findByWord(
    @Param("word") word: string
  ): Promise<KeywordResponseDto | null> {
    return this.keywordsService.findByWord(word);
  }

  @Get(":id/matches")
  @ApiOperation({ summary: "Get keyword matches and statistics" })
  @ApiParam({ name: "id", description: "Keyword ID" })
  @ApiResponse({
    status: 200,
    description: "Keyword matches information",
    schema: {
      type: "object",
      properties: {
        keyword: { $ref: "#/components/schemas/KeywordResponseDto" },
        matchesCount: { type: "number" },
        recentMatches: { type: "array" },
      },
    },
  })
  @ApiResponse({
    status: 404,
    description: "Keyword not found",
  })
  async getKeywordMatches(@Param("id") id: string) {
    return this.keywordsService.getKeywordMatches(id);
  }

  @Patch(":id")
  @ApiOperation({ summary: "Update keyword by ID" })
  @ApiParam({ name: "id", description: "Keyword ID" })
  @ApiResponse({
    status: 200,
    description: "Keyword updated successfully",
    type: KeywordResponseDto,
  })
  @ApiResponse({
    status: 404,
    description: "Keyword not found",
  })
  @ApiResponse({
    status: 409,
    description: "Keyword with this word already exists",
  })
  async update(
    @Param("id") id: string,
    @Body() updateKeywordDto: UpdateKeywordDto
  ): Promise<KeywordResponseDto> {
    return this.keywordsService.update(id, updateKeywordDto);
  }

  @Patch("bulk/status")
  @ApiOperation({ summary: "Update status for multiple keywords" })
  @ApiResponse({
    status: 200,
    description: "Keywords updated successfully",
    type: [KeywordResponseDto],
  })
  @ApiResponse({
    status: 400,
    description: "Invalid request",
  })
  async bulkUpdateStatus(
    @Body() body: { ids: string[]; isActive: boolean }
  ): Promise<KeywordResponseDto[]> {
    return this.keywordsService.bulkUpdateStatus(body.ids, body.isActive);
  }

  @Delete(":id")
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: "Delete keyword by ID" })
  @ApiParam({ name: "id", description: "Keyword ID" })
  @ApiResponse({
    status: 204,
    description: "Keyword deleted successfully",
  })
  @ApiResponse({
    status: 404,
    description: "Keyword not found",
  })
  async remove(@Param("id") id: string): Promise<void> {
    return this.keywordsService.remove(id);
  }
}
