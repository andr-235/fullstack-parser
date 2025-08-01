import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service";
import { VKCommentResponseDto } from "../../common/dto/vk-comment.dto";
import { VKComment } from "@prisma/client";

@Injectable()
export class CommentsService {
  constructor(private prisma: PrismaService) {}

  private mapToResponseDto(comment: any): VKCommentResponseDto {
    return {
      id: comment.id,
      vk_id: comment.vkId,
      group_id: comment.post?.group?.id || 0,
      group_name: comment.post?.group?.name || "",
      post_id: comment.postId,
      author_id: 0, // Default value since field doesn't exist in DB
      author_name: "Unknown Author", // Default value since field doesn't exist in DB
      author_photo: "", // Default value since field doesn't exist in DB
      text: comment.text,
      date: comment.createdAt?.toISOString() || new Date().toISOString(),
      likes_count: 0, // Default value since field doesn't exist in DB
      is_viewed: false, // Default value since field doesn't exist in DB
      is_archived: false, // Default value since field doesn't exist in DB
      keywords:
        comment.keywordMatches?.map((match: any) => match.keyword.word) || [],
      sentiment: "neutral", // Default value since field doesn't exist in DB
      created_at: comment.createdAt?.toISOString() || new Date().toISOString(),
      updated_at: comment.updatedAt?.toISOString() || new Date().toISOString(),
    };
  }

  async findAll(
    page: number = 1,
    limit: number = 20,
    search?: string,
    postId?: string,
    groupId?: string,
    hasKeywords?: boolean
  ): Promise<{
    comments: VKCommentResponseDto[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    const skip = (page - 1) * limit;

    // Build where clause
    const where: any = {};

    if (search) {
      where.text = {
        contains: search,
        mode: "insensitive",
      };
    }

    if (postId) {
      where.postId = parseInt(postId);
    }

    if (groupId) {
      where.post = {
        groupId: parseInt(groupId),
      };
    }

    if (hasKeywords !== undefined) {
      if (hasKeywords) {
        where.keywordMatches = {
          some: {},
        };
      } else {
        where.keywordMatches = {
          none: {},
        };
      }
    }

    const [comments, total] = await Promise.all([
      this.prisma.vKComment.findMany({
        where,
        skip,
        take: Number(limit),
        include: {
          keywordMatches: {
            include: {
              keyword: true,
            },
          },
          post: {
            include: {
              group: true,
            },
          },
        },
        orderBy: {
          createdAt: "desc",
        },
      }),
      this.prisma.vKComment.count({ where }),
    ]);

    const totalPages = Math.ceil(total / limit);

    return {
      comments: comments.map((comment) => this.mapToResponseDto(comment)),
      total,
      page,
      limit,
      totalPages,
    };
  }

  async findOne(id: string): Promise<VKCommentResponseDto> {
    const comment = await this.prisma.vKComment.findUnique({
      where: { id: parseInt(id) },
      include: {
        keywordMatches: {
          include: {
            keyword: true,
          },
        },
        post: {
          include: {
            group: true,
          },
        },
      },
    });

    if (!comment) {
      throw new NotFoundException(`Comment with ID ${id} not found`);
    }

    return this.mapToResponseDto(comment);
  }

  async findByPostId(postId: string): Promise<VKCommentResponseDto[]> {
    const comments = await this.prisma.vKComment.findMany({
      where: { postId: parseInt(postId) },
      include: {
        keywordMatches: {
          include: {
            keyword: true,
          },
        },
        post: {
          include: {
            group: true,
          },
        },
      },
      orderBy: {
        createdAt: "desc",
      },
    });

    return comments.map((comment) => this.mapToResponseDto(comment));
  }

  async searchByText(query: string): Promise<VKCommentResponseDto[]> {
    if (!query || query.trim().length === 0) {
      throw new BadRequestException("Search query is required");
    }

    const comments = await this.prisma.vKComment.findMany({
      where: {
        text: {
          contains: query,
          mode: "insensitive",
        },
      },
      include: {
        keywordMatches: {
          include: {
            keyword: true,
          },
        },
        post: {
          include: {
            group: true,
          },
        },
      },
      orderBy: {
        createdAt: "desc",
      },
    });

    return comments.map((comment) => this.mapToResponseDto(comment));
  }

  async create(data: {
    vkId: number;
    postId: string;
    text: string;
  }): Promise<VKCommentResponseDto> {
    const comment = await this.prisma.vKComment.create({
      data: {
        vkId: data.vkId,
        postId: parseInt(data.postId),
        text: data.text,
      },
      include: {
        keywordMatches: {
          include: {
            keyword: true,
          },
        },
        post: {
          include: {
            group: true,
          },
        },
      },
    });

    return this.mapToResponseDto(comment);
  }

  async update(
    id: string,
    data: Partial<VKComment>
  ): Promise<VKCommentResponseDto> {
    const comment = await this.prisma.vKComment.update({
      where: { id: parseInt(id) },
      data,
      include: {
        keywordMatches: {
          include: {
            keyword: true,
          },
        },
        post: {
          include: {
            group: true,
          },
        },
      },
    });

    return this.mapToResponseDto(comment);
  }

  async delete(id: string): Promise<void> {
    await this.prisma.vKComment.delete({
      where: { id: parseInt(id) },
    });
  }

  async findByGroupId(groupId: string): Promise<VKCommentResponseDto[]> {
    const comments = await this.prisma.vKComment.findMany({
      where: {
        post: {
          groupId: parseInt(groupId),
        },
      },
      include: {
        keywordMatches: {
          include: {
            keyword: true,
          },
        },
        post: {
          include: {
            group: true,
          },
        },
      },
      orderBy: {
        createdAt: "desc",
      },
    });

    return comments.map((comment) => this.mapToResponseDto(comment));
  }

  async getStatistics() {
    const [
      totalComments,
      commentsWithKeywords,
      totalKeywords,
      mostActiveGroups,
      recentComments,
    ] = await Promise.all([
      this.prisma.vKComment.count(),
      this.prisma.vKComment.count({
        where: {
          keywordMatches: {
            some: {},
          },
        },
      }),
      this.prisma.commentKeywordMatch.count(),
      this.prisma.vKComment.groupBy({
        by: ["postId"],
        _count: {
          id: true,
        },
        orderBy: {
          _count: {
            id: "desc",
          },
        },
        take: 10,
      }),
      this.prisma.vKComment.findMany({
        take: 10,
        orderBy: {
          createdAt: "desc",
        },
        include: {
          keywordMatches: {
            include: {
              keyword: true,
            },
          },
          post: {
            include: {
              group: true,
            },
          },
        },
      }),
    ]);

    return {
      totalComments,
      commentsWithKeywords,
      totalKeywords,
      averageKeywordsPerComment: totalKeywords / totalComments || 0,
      mostActiveGroups: mostActiveGroups.map((group) => ({
        postId: group.postId,
        commentCount: group._count.id,
      })),
      recentComments: recentComments.map((comment) =>
        this.mapToResponseDto(comment)
      ),
    };
  }

  async getKeywordAnalysis(limit: number = 20) {
    const keywords = await this.prisma.keyword.findMany({
      where: {
        isActive: true,
      },
      include: {
        commentMatches: true,
      },
      take: limit,
    });

    const totalKeywords = await this.prisma.keyword.count();
    const totalMatches = await this.prisma.commentKeywordMatch.count();

    const keywordStats = keywords
      .map((keyword) => ({
        word: keyword.word,
        matchCount: keyword.commentMatches.length,
        percentage: (keyword.commentMatches.length / totalMatches) * 100,
      }))
      .sort((a, b) => b.matchCount - a.matchCount);

    return {
      keywordStats,
      totalKeywords,
      totalMatches,
    };
  }

  async findByPost(postId: string, page: number = 1, limit: number = 20) {
    const skip = (page - 1) * limit;

    const [comments, total] = await Promise.all([
      this.prisma.vKComment.findMany({
        where: { postId: parseInt(postId) },
        skip,
        take: limit,
        include: {
          keywordMatches: {
            include: {
              keyword: true,
            },
          },
          post: {
            include: {
              group: true,
            },
          },
        },
        orderBy: {
          createdAt: "desc",
        },
      }),
      this.prisma.vKComment.count({
        where: { postId: parseInt(postId) },
      }),
    ]);

    const totalPages = Math.ceil(total / limit);

    return {
      comments: comments.map((comment) => this.mapToResponseDto(comment)),
      total,
      page,
      limit,
      totalPages,
    };
  }

  async findByGroup(groupId: string, page: number = 1, limit: number = 20) {
    const skip = (page - 1) * limit;

    const [comments, total] = await Promise.all([
      this.prisma.vKComment.findMany({
        where: {
          post: {
            groupId: parseInt(groupId),
          },
        },
        skip,
        take: limit,
        include: {
          keywordMatches: {
            include: {
              keyword: true,
            },
          },
          post: {
            include: {
              group: true,
            },
          },
        },
        orderBy: {
          createdAt: "desc",
        },
      }),
      this.prisma.vKComment.count({
        where: {
          post: {
            groupId: parseInt(groupId),
          },
        },
      }),
    ]);

    const totalPages = Math.ceil(total / limit);

    return {
      comments: comments.map((comment) => this.mapToResponseDto(comment)),
      total,
      page,
      limit,
      totalPages,
    };
  }

  async getCommentsByKeyword(
    keyword: string,
    page: number = 1,
    limit: number = 20
  ) {
    const skip = (page - 1) * limit;

    const [comments, total] = await Promise.all([
      this.prisma.vKComment.findMany({
        where: {
          keywordMatches: {
            some: {
              keyword: {
                word: keyword,
              },
            },
          },
        },
        skip,
        take: limit,
        include: {
          keywordMatches: {
            include: {
              keyword: true,
            },
          },
          post: {
            include: {
              group: true,
            },
          },
        },
        orderBy: {
          createdAt: "desc",
        },
      }),
      this.prisma.vKComment.count({
        where: {
          keywordMatches: {
            some: {
              keyword: {
                word: keyword,
              },
            },
          },
        },
      }),
    ]);

    const totalPages = Math.ceil(total / limit);

    return {
      comments: comments.map((comment) => this.mapToResponseDto(comment)),
      total,
      page,
      limit,
      totalPages,
    };
  }

  async getCommentsByDateRange(
    startDate: Date,
    endDate: Date,
    page: number = 1,
    limit: number = 20
  ) {
    const skip = (page - 1) * limit;

    const [comments, total] = await Promise.all([
      this.prisma.vKComment.findMany({
        where: {
          createdAt: {
            gte: startDate,
            lte: endDate,
          },
        },
        skip,
        take: limit,
        include: {
          keywordMatches: {
            include: {
              keyword: true,
            },
          },
          post: {
            include: {
              group: true,
            },
          },
        },
        orderBy: {
          createdAt: "desc",
        },
      }),
      this.prisma.vKComment.count({
        where: {
          createdAt: {
            gte: startDate,
            lte: endDate,
          },
        },
      }),
    ]);

    const totalPages = Math.ceil(total / limit);

    return {
      comments: comments.map((comment) => this.mapToResponseDto(comment)),
      total,
      page,
      limit,
      totalPages,
    };
  }
}
