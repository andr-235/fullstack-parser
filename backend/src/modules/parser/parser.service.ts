import {
  Injectable,
  Logger,
  BadRequestException,
  NotFoundException,
} from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service";
import { VkApiService } from "./vk-api.service";
import { VKGroup, VKPost, VKComment, Keyword } from "@prisma/client";

@Injectable()
export class ParserService {
  private readonly logger = new Logger(ParserService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly vkApiService: VkApiService
  ) {}

  async parseGroup(screenName: string): Promise<VKGroup> {
    try {
      this.logger.log(`Starting to parse group: ${screenName}`);

      // Validate screen name
      if (!screenName || screenName.trim().length === 0) {
        throw new BadRequestException("Screen name is required");
      }

      // Get group info from VK API
      const group = await this.vkApiService.getGroup(screenName);

      if (!group) {
        throw new NotFoundException(`Group not found: ${screenName}`);
      }

      // Create or update group in database
      const existingGroup = await this.prisma.vKGroup.findUnique({
        where: { vkId: group.id },
      });

      if (existingGroup) {
        this.logger.log(`Updating existing group: ${group.name}`);
        return this.prisma.vKGroup.update({
          where: { id: existingGroup.id },
          data: {
            name: group.name,
            screenName: group.screen_name,
            updatedAt: new Date(),
          },
        });
      } else {
        this.logger.log(`Creating new group: ${group.name}`);
        return this.prisma.vKGroup.create({
          data: {
            vkId: group.id,
            screenName: group.screen_name,
            name: group.name,
          },
        });
      }
    } catch (error) {
      this.logger.error(`Error parsing group ${screenName}:`, error);
      throw error;
    }
  }

  async parseGroupPosts(
    groupId: string,
    limit: number = 100
  ): Promise<VKPost[]> {
    try {
      this.logger.log(`Starting to parse posts for group: ${groupId}`);

      if (limit < 1 || limit > 1000) {
        throw new BadRequestException("Limit must be between 1 and 1000");
      }

      const group = await this.prisma.vKGroup.findUnique({
        where: { id: groupId },
      });

      if (!group) {
        throw new NotFoundException(`Group not found: ${groupId}`);
      }

      // Get posts from VK API
      const postsData = await this.vkApiService.getWallPosts(
        group.vkId,
        limit
      );

      if (!postsData.items || postsData.items.length === 0) {
        this.logger.warn(`No posts found for group: ${groupId}`);
        return [];
      }

      const posts: VKPost[] = [];
      const batchSize = 10; // Process in batches to avoid overwhelming the database

      for (let i = 0; i < postsData.items.length; i += batchSize) {
        const batch = postsData.items.slice(i, i + batchSize);

        for (const post of batch) {
          try {
            // Check if post already exists
            const existingPost = await this.prisma.vKPost.findUnique({
              where: { vkId: post.id },
            });

            if (!existingPost) {
              const createdPost = await this.prisma.vKPost.create({
                data: {
                  vkId: post.id,
                  groupId: group.id,
                  text: post.text || "",
                },
              });
              posts.push(createdPost);
            }
          } catch (error) {
            this.logger.error(`Error processing post ${post.id}:`, error);
            // Continue with other posts
          }
        }
      }

      this.logger.log(`Parsed ${posts.length} new posts for group: ${groupId}`);
      return posts;
    } catch (error) {
      this.logger.error(`Error parsing posts for group ${groupId}:`, error);
      throw error;
    }
  }

  async parsePostComments(
    postId: string,
    limit: number = 100
  ): Promise<VKComment[]> {
    try {
      this.logger.log(`Starting to parse comments for post: ${postId}`);

      if (limit < 1 || limit > 1000) {
        throw new BadRequestException("Limit must be between 1 and 1000");
      }

      const post = await this.prisma.vKPost.findUnique({
        where: { id: postId },
        include: { group: true },
      });

      if (!post) {
        throw new NotFoundException(`Post not found: ${postId}`);
      }

      // Get comments from VK API
      const commentsData = await this.vkApiService.getPostComments(
        -post.group.vkId,
        post.vkId,
        limit
      );

      if (!commentsData.items || commentsData.items.length === 0) {
        this.logger.warn(`No comments found for post: ${postId}`);
        return [];
      }

      const comments: VKComment[] = [];
      const batchSize = 10;

      for (let i = 0; i < commentsData.items.length; i += batchSize) {
        const batch = commentsData.items.slice(i, i + batchSize);

        for (const comment of batch) {
          try {
            // Check if comment already exists
            const existingComment = await this.prisma.vKComment.findUnique({
              where: { vkId: comment.id },
            });

            if (!existingComment) {
              const createdComment = await this.prisma.vKComment.create({
                data: {
                  vkId: comment.id,
                  postId: post.id,
                  text: comment.text || "",
                },
              });
              comments.push(createdComment);
            }
          } catch (error) {
            this.logger.error(`Error processing comment ${comment.id}:`, error);
            // Continue with other comments
          }
        }
      }

      this.logger.log(
        `Parsed ${comments.length} new comments for post: ${postId}`
      );
      return comments;
    } catch (error) {
      this.logger.error(`Error parsing comments for post ${postId}:`, error);
      throw error;
    }
  }

  async matchKeywordsForComment(commentId: string): Promise<void> {
    try {
      this.logger.log(`Starting keyword matching for comment: ${commentId}`);

      const comment = await this.prisma.vKComment.findUnique({
        where: { id: commentId },
      });

      if (!comment) {
        throw new NotFoundException(`Comment not found: ${commentId}`);
      }

      // Get all active keywords
      const keywords = await this.prisma.keyword.findMany({
        where: { isActive: true },
      });

      if (keywords.length === 0) {
        this.logger.log("No active keywords found for matching");
        return;
      }

      const commentText = comment.text.toLowerCase();
      const matchedKeywords: Keyword[] = [];

      // Check each keyword against the comment text
      for (const keyword of keywords) {
        if (commentText.includes(keyword.word.toLowerCase())) {
          matchedKeywords.push(keyword);
        }
      }

      // Create keyword matches
      for (const keyword of matchedKeywords) {
        try {
          await this.prisma.commentKeywordMatch.create({
            data: {
              commentId: comment.id,
              keywordId: keyword.id,
            },
          });
        } catch (error) {
          // Ignore duplicate matches
          if (error.code !== "P2002") {
            this.logger.error(`Error creating keyword match:`, error);
          }
        }
      }

      this.logger.log(
        `Matched ${matchedKeywords.length} keywords for comment: ${commentId}`
      );
    } catch (error) {
      this.logger.error(
        `Error matching keywords for comment ${commentId}:`,
        error
      );
      throw error;
    }
  }

  async matchKeywordsForAllComments(): Promise<void> {
    try {
      this.logger.log("Starting keyword matching for all comments");

      const comments = await this.prisma.vKComment.findMany({
        where: {
          keywordMatches: {
            none: {}, // Comments without any keyword matches
          },
        },
      });

      this.logger.log(
        `Found ${comments.length} comments without keyword matches`
      );

      for (const comment of comments) {
        try {
          await this.matchKeywordsForComment(comment.id);
        } catch (error) {
          this.logger.error(
            `Error matching keywords for comment ${comment.id}:`,
            error
          );
          // Continue with other comments
        }
      }

      this.logger.log("Completed keyword matching for all comments");
    } catch (error) {
      this.logger.error("Error in batch keyword matching:", error);
      throw error;
    }
  }

  async getParsingStats(): Promise<{
    totalGroups: number;
    totalPosts: number;
    totalComments: number;
    totalKeywords: number;
    totalMatches: number;
  }> {
    try {
      const [groups, posts, comments, keywords, matches] = await Promise.all([
        this.prisma.vKGroup.count(),
        this.prisma.vKPost.count(),
        this.prisma.vKComment.count(),
        this.prisma.keyword.count(),
        this.prisma.commentKeywordMatch.count(),
      ]);

      return {
        totalGroups: groups,
        totalPosts: posts,
        totalComments: comments,
        totalKeywords: keywords,
        totalMatches: matches,
      };
    } catch (error) {
      this.logger.error("Error getting parsing stats:", error);
      throw error;
    }
  }

  async getGroupStats(groupId: string): Promise<{
    group: VKGroup;
    postsCount: number;
    commentsCount: number;
    matchesCount: number;
  }> {
    try {
      const group = await this.prisma.vKGroup.findUnique({
        where: { id: groupId },
      });

      if (!group) {
        throw new NotFoundException(`Group not found: ${groupId}`);
      }

      const [postsCount, commentsCount, matchesCount] = await Promise.all([
        this.prisma.vKPost.count({
          where: { groupId },
        }),
        this.prisma.vKComment.count({
          where: {
            post: {
              groupId,
            },
          },
        }),
        this.prisma.commentKeywordMatch.count({
          where: {
            comment: {
              post: {
                groupId,
              },
            },
          },
        }),
      ]);

      return {
        group,
        postsCount,
        commentsCount,
        matchesCount,
      };
    } catch (error) {
      this.logger.error(`Error getting group stats for ${groupId}:`, error);
      throw error;
    }
  }
}
