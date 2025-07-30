import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service";
import { VKComment } from "@prisma/client";
import { VKCommentResponseDto } from "../../common/dto";

@Injectable()
export class CommentsService {
  constructor(private prisma: PrismaService) {}

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
      where.postId = postId;
    }

    if (groupId) {
      where.post = {
        groupId: groupId,
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
      comments: comments.map((comment) => ({
        id: comment.id,
        vkId: comment.vkId,
        postId: comment.postId,
        text: comment.text,
        createdAt: comment.createdAt,
        updatedAt: comment.updatedAt,
        keywords: comment.keywordMatches.map((match) => match.keyword.word),
        post: comment.post,
      })),
      total,
      page,
      limit,
      totalPages,
    };
  }

  async findOne(id: string): Promise<VKCommentResponseDto> {
    const comment = await this.prisma.vKComment.findUnique({
      where: { id },
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

    return {
      id: comment.id,
      vkId: comment.vkId,
      postId: comment.postId,
      text: comment.text,
      createdAt: comment.createdAt,
      updatedAt: comment.updatedAt,
      keywords: comment.keywordMatches.map((match) => match.keyword.word),
      post: comment.post,
    };
  }

  async findByPostId(postId: string): Promise<VKCommentResponseDto[]> {
    const comments = await this.prisma.vKComment.findMany({
      where: { postId },
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

    return comments.map((comment) => ({
      id: comment.id,
      vkId: comment.vkId,
      postId: comment.postId,
      text: comment.text,
      createdAt: comment.createdAt,
      updatedAt: comment.updatedAt,
      keywords: comment.keywordMatches.map((match) => match.keyword.word),
      post: comment.post,
    }));
  }

  async searchByText(query: string): Promise<VKCommentResponseDto[]> {
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
    });

    return comments.map((comment) => ({
      id: comment.id,
      vkId: comment.vkId,
      postId: comment.postId,
      text: comment.text,
      createdAt: comment.createdAt,
      updatedAt: comment.updatedAt,
      keywords: comment.keywordMatches.map((match) => match.keyword.word),
      post: comment.post,
    }));
  }

  async create(data: {
    vkId: number;
    postId: string;
    text: string;
  }): Promise<VKCommentResponseDto> {
    const comment = await this.prisma.vKComment.create({
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

    return {
      id: comment.id,
      vkId: comment.vkId,
      postId: comment.postId,
      text: comment.text,
      createdAt: comment.createdAt,
      updatedAt: comment.updatedAt,
      keywords: comment.keywordMatches.map((match) => match.keyword.word),
      post: comment.post,
    };
  }

  async update(
    id: string,
    data: Partial<VKComment>
  ): Promise<VKCommentResponseDto> {
    const comment = await this.prisma.vKComment.update({
      where: { id },
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

    return {
      id: comment.id,
      vkId: comment.vkId,
      postId: comment.postId,
      text: comment.text,
      createdAt: comment.createdAt,
      updatedAt: comment.updatedAt,
      keywords: comment.keywordMatches.map((match) => match.keyword.word),
      post: comment.post,
    };
  }

  async delete(id: string): Promise<void> {
    await this.prisma.vKComment.delete({
      where: { id },
    });
  }

  async findByGroupId(groupId: string): Promise<VKCommentResponseDto[]> {
    const comments = await this.prisma.vKComment.findMany({
      where: {
        post: {
          groupId,
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
    });

    return comments.map((comment) => ({
      id: comment.id,
      vkId: comment.vkId,
      postId: comment.postId,
      text: comment.text,
      createdAt: comment.createdAt,
      updatedAt: comment.updatedAt,
      keywords: comment.keywordMatches.map((match) => match.keyword.word),
      post: comment.post,
    }));
  }

  async getStatistics() {
    const [
      totalComments,
      commentsWithKeywords,
      averageCommentsPerPost,
      topGroups,
    ] = await Promise.all([
      this.prisma.vKComment.count(),
      this.prisma.vKComment.count({
        where: {
          keywordMatches: {
            some: {},
          },
        },
      }),
      this.prisma.vKComment
        .groupBy({
          by: ["postId"],
          _count: {
            id: true,
          },
        })
        .then((result) => {
          const totalPosts = result.length;
          const totalComments = result.reduce(
            (sum, group) => sum + group._count.id,
            0
          );
          return totalPosts > 0 ? totalComments / totalPosts : 0;
        }),
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
    ]);

    // Get group information for top posts
    const postIds = topGroups.map((group) => group.postId);
    const posts = await this.prisma.vKPost.findMany({
      where: {
        id: {
          in: postIds,
        },
      },
      include: {
        group: true,
      },
    });

    const topGroupsWithNames = topGroups.map((group) => {
      const post = posts.find((p) => p.id === group.postId);
      return {
        groupId: post?.groupId || "Unknown",
        groupName: post?.group?.name || "Unknown",
        commentCount: group._count.id,
      };
    });

    return {
      totalComments,
      commentsWithKeywords,
      averageCommentsPerPost,
      topGroups: topGroupsWithNames,
    };
  }

  async getKeywordAnalysis(limit: number = 20) {
    const [totalComments, totalCommentsWithKeywords, keywordMatches] =
      await Promise.all([
        this.prisma.vKComment.count(),
        this.prisma.vKComment.count({
          where: {
            keywordMatches: {
              some: {},
            },
          },
        }),
        this.prisma.commentKeywordMatch.findMany({
          include: {
            keyword: true,
          },
        }),
      ]);

    // Count keyword frequency
    const keywordCounts = new Map<string, number>();
    keywordMatches.forEach((match) => {
      const count = keywordCounts.get(match.keyword.word) || 0;
      keywordCounts.set(match.keyword.word, count + 1);
    });

    // Convert to array and sort by frequency
    const sortedKeywords = Array.from(keywordCounts.entries())
      .map(([keyword, count]) => ({
        keyword,
        count,
        percentage: (count / totalCommentsWithKeywords) * 100,
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, limit);

    return {
      keywordFrequency: sortedKeywords,
      totalCommentsWithKeywords,
      totalComments,
    };
  }

  async findByPost(postId: string, page: number = 1, limit: number = 20) {
    const skip = (page - 1) * limit;

    const [comments, total] = await Promise.all([
      this.prisma.vKComment.findMany({
        where: { postId },
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
        where: { postId },
      }),
    ]);

    const totalPages = Math.ceil(total / limit);

    return {
      comments: comments.map((comment) => ({
        id: comment.id,
        vkId: comment.vkId,
        postId: comment.postId,
        text: comment.text,
        createdAt: comment.createdAt,
        updatedAt: comment.updatedAt,
        keywords: comment.keywordMatches.map((match) => match.keyword.word),
        post: comment.post,
      })),
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
            groupId,
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
            groupId,
          },
        },
      }),
    ]);

    const totalPages = Math.ceil(total / limit);

    return {
      comments: comments.map((comment) => ({
        id: comment.id,
        vkId: comment.vkId,
        postId: comment.postId,
        text: comment.text,
        createdAt: comment.createdAt,
        updatedAt: comment.updatedAt,
        keywords: comment.keywordMatches.map((match) => match.keyword.word),
        post: comment.post,
      })),
      total,
      page,
      limit,
      totalPages,
    };
  }
}
