import {
  Injectable,
  NotFoundException,
  ConflictException,
  BadRequestException,
} from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service";
import { Keyword } from "@prisma/client";
import {
  CreateKeywordDto,
  UpdateKeywordDto,
  KeywordResponseDto,
} from "../../common/dto";

@Injectable()
export class KeywordsService {
  constructor(private prisma: PrismaService) {}

  async create(
    createKeywordDto: CreateKeywordDto
  ): Promise<KeywordResponseDto> {
    // Check if keyword already exists
    const existingKeyword = await this.prisma.keyword.findUnique({
      where: { word: createKeywordDto.word.toLowerCase() },
    });

    if (existingKeyword) {
      throw new ConflictException("Keyword already exists");
    }

    const keyword = await this.prisma.keyword.create({
      data: {
        word: createKeywordDto.word.toLowerCase(),
        isActive: createKeywordDto.isActive ?? true,
      },
    });

    return this.mapToResponseDto(keyword);
  }

  async findAll(
    page: number = 1,
    limit: number = 20,
    search?: string,
    isActive?: boolean
  ): Promise<{
    keywords: KeywordResponseDto[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    const skip = (page - 1) * limit;

    // Build where clause
    const where: any = {};
    if (search) {
      where.word = {
        contains: search.toLowerCase(),
        mode: "insensitive",
      };
    }
    if (isActive !== undefined) {
      where.isActive = isActive;
    }

    const [keywords, total] = await Promise.all([
      this.prisma.keyword.findMany({
        where,
        skip,
        take: limit,
        orderBy: { createdAt: "desc" },
      }),
      this.prisma.keyword.count({ where }),
    ]);

    return {
      keywords: keywords.map((keyword) => this.mapToResponseDto(keyword)),
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit),
    };
  }

  async findOne(id: string): Promise<KeywordResponseDto> {
    const keyword = await this.prisma.keyword.findUnique({
      where: { id },
    });

    if (!keyword) {
      throw new NotFoundException(`Keyword with ID ${id} not found`);
    }

    return this.mapToResponseDto(keyword);
  }

  async findByWord(word: string): Promise<KeywordResponseDto | null> {
    const keyword = await this.prisma.keyword.findUnique({
      where: { word: word.toLowerCase() },
    });

    return keyword ? this.mapToResponseDto(keyword) : null;
  }

  async update(
    id: string,
    updateKeywordDto: UpdateKeywordDto
  ): Promise<KeywordResponseDto> {
    // Check if keyword exists
    const existingKeyword = await this.prisma.keyword.findUnique({
      where: { id },
    });

    if (!existingKeyword) {
      throw new NotFoundException(`Keyword with ID ${id} not found`);
    }

    // If word is being updated, check for conflicts
    if (
      updateKeywordDto.word &&
      updateKeywordDto.word !== existingKeyword.word
    ) {
      const wordConflict = await this.prisma.keyword.findUnique({
        where: { word: updateKeywordDto.word.toLowerCase() },
      });

      if (wordConflict) {
        throw new ConflictException("Keyword with this word already exists");
      }
    }

    // Prepare update data
    const updateData: any = {};

    if (updateKeywordDto.word) {
      updateData.word = updateKeywordDto.word.toLowerCase();
    }
    if (updateKeywordDto.isActive !== undefined) {
      updateData.isActive = updateKeywordDto.isActive;
    }

    const keyword = await this.prisma.keyword.update({
      where: { id },
      data: updateData,
    });

    return this.mapToResponseDto(keyword);
  }

  async remove(id: string): Promise<void> {
    const keyword = await this.prisma.keyword.findUnique({
      where: { id },
    });

    if (!keyword) {
      throw new NotFoundException(`Keyword with ID ${id} not found`);
    }

    await this.prisma.keyword.delete({
      where: { id },
    });
  }

  async bulkCreate(keywords: string[]): Promise<KeywordResponseDto[]> {
    if (!keywords || keywords.length === 0) {
      throw new BadRequestException("Keywords array cannot be empty");
    }

    if (keywords.length > 100) {
      throw new BadRequestException(
        "Cannot create more than 100 keywords at once"
      );
    }

    const createdKeywords: KeywordResponseDto[] = [];
    const errors: string[] = [];

    for (const word of keywords) {
      try {
        const keyword = await this.create({ word: word.trim() });
        createdKeywords.push(keyword);
      } catch (error) {
        if (error instanceof ConflictException) {
          errors.push(`Keyword "${word}" already exists`);
        } else {
          errors.push(`Failed to create keyword "${word}": ${error.message}`);
        }
      }
    }

    if (errors.length > 0) {
      // Log errors but don't fail the entire operation
      console.warn("Some keywords failed to create:", errors);
    }

    return createdKeywords;
  }

  async bulkUpdateStatus(
    ids: string[],
    isActive: boolean
  ): Promise<KeywordResponseDto[]> {
    if (!ids || ids.length === 0) {
      throw new BadRequestException("IDs array cannot be empty");
    }

    if (ids.length > 100) {
      throw new BadRequestException(
        "Cannot update more than 100 keywords at once"
      );
    }

    const updatedKeywords = await this.prisma.keyword.updateMany({
      where: {
        id: {
          in: ids,
        },
      },
      data: {
        isActive,
      },
    });

    // Return updated keywords
    const keywords = await this.prisma.keyword.findMany({
      where: {
        id: {
          in: ids,
        },
      },
    });

    return keywords.map((keyword) => this.mapToResponseDto(keyword));
  }

  async getKeywordStats(): Promise<{
    totalKeywords: number;
    activeKeywords: number;
    inactiveKeywords: number;
    totalMatches: number;
    averageMatchesPerKeyword: number;
  }> {
    const [totalKeywords, activeKeywords, totalMatches] = await Promise.all([
      this.prisma.keyword.count(),
      this.prisma.keyword.count({
        where: { isActive: true },
      }),
      this.prisma.commentKeywordMatch.count(),
    ]);

    const inactiveKeywords = totalKeywords - activeKeywords;
    const averageMatchesPerKeyword =
      totalKeywords > 0 ? totalMatches / totalKeywords : 0;

    return {
      totalKeywords,
      activeKeywords,
      inactiveKeywords,
      totalMatches,
      averageMatchesPerKeyword:
        Math.round(averageMatchesPerKeyword * 100) / 100,
    };
  }

  async getKeywordMatches(keywordId: string): Promise<{
    keyword: KeywordResponseDto;
    matchesCount: number;
    recentMatches: any[];
  }> {
    const keyword = await this.prisma.keyword.findUnique({
      where: { id: keywordId },
    });

    if (!keyword) {
      throw new NotFoundException(`Keyword with ID ${keywordId} not found`);
    }

    const [matchesCount, recentMatches] = await Promise.all([
      this.prisma.commentKeywordMatch.count({
        where: { keywordId },
      }),
      this.prisma.commentKeywordMatch.findMany({
        where: { keywordId },
        include: {
          comment: {
            include: {
              post: {
                include: {
                  group: true,
                },
              },
            },
          },
        },
        orderBy: { createdAt: "desc" },
        take: 10,
      }),
    ]);

    return {
      keyword: this.mapToResponseDto(keyword),
      matchesCount,
      recentMatches,
    };
  }

  async searchKeywords(
    query: string,
    limit: number = 20
  ): Promise<KeywordResponseDto[]> {
    if (!query || query.trim().length === 0) {
      throw new BadRequestException("Search query is required");
    }

    if (limit < 1 || limit > 100) {
      throw new BadRequestException("Limit must be between 1 and 100");
    }

    const keywords = await this.prisma.keyword.findMany({
      where: {
        word: {
          contains: query.toLowerCase(),
          mode: "insensitive",
        },
      },
      take: limit,
      orderBy: { createdAt: "desc" },
    });

    return keywords.map((keyword) => this.mapToResponseDto(keyword));
  }

  async getTopKeywords(limit: number = 10): Promise<
    {
      keyword: KeywordResponseDto;
      matchesCount: number;
    }[]
  > {
    if (limit < 1 || limit > 100) {
      throw new BadRequestException("Limit must be between 1 and 100");
    }

    const topKeywords = await this.prisma.keyword.findMany({
      include: {
        _count: {
          select: {
            commentMatches: true,
          },
        },
      },
      orderBy: {
        commentMatches: {
          _count: "desc",
        },
      },
      take: limit,
    });

    return topKeywords.map((keyword) => ({
      keyword: this.mapToResponseDto(keyword),
      matchesCount: keyword._count.commentMatches,
    }));
  }

  private mapToResponseDto(keyword: Keyword): KeywordResponseDto {
    return {
      id: keyword.id,
      word: keyword.word,
      isActive: keyword.isActive,
      createdAt: keyword.createdAt,
      updatedAt: keyword.updatedAt,
    };
  }
}
