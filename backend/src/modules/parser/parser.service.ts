import {
  Injectable,
  Logger,
  BadRequestException,
  NotFoundException,
} from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service";
import { VkApiService } from "./vk-api.service";
import { RedisService } from "../../common/redis";
import { VKGroup, VKPost, VKComment, Keyword } from "@prisma/client";
import { VKGroupDto, VKPostDto, VKCommentDto } from "../../common/dto/vk.dto";
import {
  ParseTaskCreate,
  ParseTaskResponse,
  ParseTaskStatus,
} from "../../common/dto/parser.dto";

@Injectable()
export class ParserService {
  private readonly logger = new Logger(ParserService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly vkApiService: VkApiService,
    private readonly redisService: RedisService
  ) {}

  private mapGroupToDto(group: VKGroup): VKGroupDto {
    return {
      id: group.id.toString(),
      vkId: group.vkId,
      screenName: group.screenName,
      name: group.name,
      description: group.description,
      isActive: group.isActive,
      createdAt: group.createdAt,
      updatedAt: group.updatedAt,
    };
  }

  private mapPostToDto(post: VKPost): VKPostDto {
    return {
      id: post.id.toString(),
      vkId: post.vkId,
      text: post.text,
      createdAt: post.createdAt,
      updatedAt: post.updatedAt,
      groupId: post.groupId.toString(),
    };
  }

  private mapCommentToDto(comment: VKComment): VKCommentDto {
    return {
      id: comment.id.toString(),
      vkId: comment.vkId,
      text: comment.text,
      createdAt: comment.createdAt,
      updatedAt: comment.updatedAt,
      postId: comment.postId.toString(),
    };
  }

  async parseGroup(screenName: string): Promise<VKGroupDto> {
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

      let dbGroup: VKGroup;

      if (existingGroup) {
        this.logger.log(`Updating existing group: ${group.name}`);
        dbGroup = await this.prisma.vKGroup.update({
          where: { id: existingGroup.id },
          data: {
            name: group.name,
            screenName: group.screen_name,
            updatedAt: new Date(),
          },
        });
      } else {
        this.logger.log(`Creating new group: ${group.name}`);
        dbGroup = await this.prisma.vKGroup.create({
          data: {
            vkId: group.id,
            screenName: group.screen_name,
            name: group.name,
          },
        });
      }

      return this.mapGroupToDto(dbGroup);
    } catch (error) {
      this.logger.error(`Error parsing group ${screenName}:`, error);
      throw error;
    }
  }

  async getGroupById(groupId: string): Promise<VKGroupDto> {
    try {
      this.logger.log(`Getting group by ID: ${groupId}`);

      const group = await this.prisma.vKGroup.findUnique({
        where: { id: parseInt(groupId) },
      });

      if (!group) {
        throw new NotFoundException(`Group not found with ID: ${groupId}`);
      }

      return this.mapGroupToDto(group);
    } catch (error) {
      this.logger.error(`Error getting group by ID ${groupId}:`, error);
      throw error;
    }
  }

  async parseGroupPosts(
    groupId: string,
    limit: number = 100
  ): Promise<VKPostDto[]> {
    try {
      this.logger.log(`Starting to parse posts for group: ${groupId}`);

      if (limit < 1 || limit > 1000) {
        throw new BadRequestException("Limit must be between 1 and 1000");
      }

      const group = await this.prisma.vKGroup.findUnique({
        where: { id: parseInt(groupId) },
      });

      if (!group) {
        throw new NotFoundException(`Group not found: ${groupId}`);
      }

      // Get posts from VK API
      const postsData = await this.vkApiService.getWallPosts(group.vkId, limit);

      if (!postsData.items || postsData.items.length === 0) {
        this.logger.warn(`No posts found for group: ${groupId}`);
        return [];
      }

      const posts: VKPostDto[] = [];
      const batchSize = 10; // Process in batches to avoid overwhelming the database

      for (let i = 0; i < postsData.items.length; i += batchSize) {
        const batch = postsData.items.slice(i, i + batchSize);

        for (const postData of batch) {
          try {
            // Check if post already exists
            const existingPost = await this.prisma.vKPost.findUnique({
              where: { vkId: postData.id },
            });

            if (existingPost) {
              this.logger.debug(`Post ${postData.id} already exists, skipping`);
              posts.push(this.mapPostToDto(existingPost));
              continue;
            }

            // Create new post
            const post = await this.prisma.vKPost.create({
              data: {
                vkId: postData.id,
                text: postData.text || "",
                groupId: group.id,
              },
            });

            posts.push(this.mapPostToDto(post));
            this.logger.debug(`Created post: ${postData.id}`);
          } catch (error) {
            this.logger.error(`Error processing post ${postData.id}:`, error);
            // Continue with other posts
          }
        }
      }

      this.logger.log(
        `Successfully parsed ${posts.length} posts for group: ${groupId}`
      );
      return posts;
    } catch (error) {
      this.logger.error(`Error parsing posts for group ${groupId}:`, error);
      // Return empty array instead of throwing error for VK API issues
      if (
        error.message &&
        (error.message.includes("User was deleted or banned") ||
          error.message.includes("This profile is private"))
      ) {
        this.logger.warn(
          `Group ${groupId} is deleted, banned, or private, returning empty posts array`
        );
        return [];
      }
      throw error;
    }
  }

  async parsePostComments(
    postId: string,
    limit: number = 100
  ): Promise<VKCommentDto[]> {
    try {
      this.logger.log(`Starting to parse comments for post: ${postId}`);

      if (limit < 1 || limit > 1000) {
        throw new BadRequestException("Limit must be between 1 and 1000");
      }

      const post = await this.prisma.vKPost.findUnique({
        where: { id: parseInt(postId) },
      });

      if (!post) {
        throw new NotFoundException(`Post not found: ${postId}`);
      }

      // Get comments from VK API
      const commentsData = await this.vkApiService.getWallPosts(
        post.groupId,
        limit
      );

      if (!commentsData.items || commentsData.items.length === 0) {
        this.logger.warn(`No comments found for post: ${postId}`);
        return [];
      }

      const comments: VKCommentDto[] = [];
      const batchSize = 10;

      for (let i = 0; i < commentsData.items.length; i += batchSize) {
        const batch = commentsData.items.slice(i, i + batchSize);

        for (const commentData of batch) {
          try {
            // Check if comment already exists
            const existingComment = await this.prisma.vKComment.findUnique({
              where: { vkId: commentData.id },
            });

            if (existingComment) {
              this.logger.debug(
                `Comment ${commentData.id} already exists, skipping`
              );
              comments.push(this.mapCommentToDto(existingComment));
              continue;
            }

            // Create new comment
            const comment = await this.prisma.vKComment.create({
              data: {
                vkId: commentData.id,
                text: commentData.text || "",
                postId: post.id,
              },
            });

            comments.push(this.mapCommentToDto(comment));
            this.logger.debug(`Created comment: ${commentData.id}`);
          } catch (error) {
            this.logger.error(
              `Error processing comment ${commentData.id}:`,
              error
            );
            // Continue with other comments
          }
        }
      }

      this.logger.log(
        `Successfully parsed ${comments.length} comments for post: ${postId}`
      );
      return comments;
    } catch (error) {
      this.logger.error(`Error parsing comments for post ${postId}:`, error);
      // Return empty array instead of throwing error for VK API issues
      if (
        error.message &&
        (error.message.includes("User was deleted or banned") ||
          error.message.includes("This profile is private"))
      ) {
        this.logger.warn(
          `Post ${postId} is from deleted/banned/private group, returning empty comments array`
        );
        return [];
      }
      throw error;
    }
  }

  async matchKeywordsForComment(commentId: string): Promise<void> {
    try {
      this.logger.log(`Starting keyword matching for comment: ${commentId}`);

      const comment = await this.prisma.vKComment.findUnique({
        where: { id: parseInt(commentId) },
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
          await this.matchKeywordsForComment(comment.id.toString());
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
    group: VKGroupDto;
    postsCount: number;
    commentsCount: number;
    matchesCount: number;
  }> {
    const group = await this.prisma.vKGroup.findUnique({
      where: { id: parseInt(groupId) },
    });

    if (!group) {
      throw new NotFoundException(`Group not found: ${groupId}`);
    }

    const [postsCount, commentsCount, matchesCount] = await Promise.all([
      this.prisma.vKPost.count({
        where: { groupId: group.id },
      }),
      this.prisma.vKComment.count({
        where: {
          post: {
            groupId: group.id,
          },
        },
      }),
      this.prisma.commentKeywordMatch.count({
        where: {
          comment: {
            post: {
              groupId: group.id,
            },
          },
        },
      }),
    ]);

    return {
      group: this.mapGroupToDto(group),
      postsCount,
      commentsCount,
      matchesCount,
    };
  }

  async fullParseGroup(
    groupId: string,
    postsLimit: number = 100,
    commentsLimit: number = 100
  ): Promise<{
    group: VKGroupDto;
    postsParsed: number;
    commentsParsed: number;
    keywordsMatched: number;
  }> {
    try {
      // Get existing group by ID
      const group = await this.getGroupById(groupId);

      // Parse posts
      const posts = await this.parseGroupPosts(group.id, postsLimit);

      // Parse comments for each post
      let totalComments = 0;
      for (const post of posts) {
        const comments = await this.parsePostComments(post.id, commentsLimit);
        totalComments += comments.length;
      }

      // Match keywords for all comments
      await this.matchKeywordsForAllComments();

      // Get final stats
      const stats = await this.getGroupStats(group.id);

      return {
        group,
        postsParsed: posts.length,
        commentsParsed: totalComments,
        keywordsMatched: stats.matchesCount,
      };
    } catch (error) {
      this.logger.error(`Error in fullParseGroup for group ${groupId}:`, error);
      throw error;
    }
  }

  // Task Queue Management
  async createParseTask(taskData: ParseTaskCreate): Promise<ParseTaskResponse> {
    try {
      const taskId = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

      const task: ParseTaskResponse = {
        id: taskId,
        status: "pending",
        totalGroups: taskData.groupIds.length,
        processedGroups: 0,
        progress: 0,
        createdAt: new Date(),
      };

      // Store task in Redis
      await this.redisService.setTaskStatus(taskId, task);
      await this.redisService.setTaskProgress(taskId, 0);

      // Start processing in background
      this.processParseTask(taskId, taskData);

      return task;
    } catch (error) {
      this.logger.error("Error creating parse task:", error);
      throw error;
    }
  }

  async getParseTaskStatus(taskId: string): Promise<ParseTaskStatus> {
    try {
      const status = await this.redisService.getTaskStatus(taskId);
      const progress = await this.redisService.getTaskProgress(taskId);
      const currentGroup = await this.redisService.hGet(
        `task:${taskId}`,
        "currentGroup"
      );
      const processedGroups = await this.redisService.hGet(
        `task:${taskId}`,
        "processedGroups"
      );
      const error = await this.redisService.hGet(`task:${taskId}`, "error");
      const results = await this.redisService.hGet(`task:${taskId}`, "results");
      const completedAt = await this.redisService.hGet(
        `task:${taskId}`,
        "completedAt"
      );

      if (!status) {
        throw new Error("Task not found");
      }

      return {
        id: taskId,
        status: status.status,
        totalGroups: status.totalGroups,
        processedGroups: processedGroups ? parseInt(processedGroups) : 0,
        currentGroup: currentGroup || undefined,
        progress: progress || 0,
        createdAt: status.createdAt || new Date(),
        completedAt: completedAt ? new Date(completedAt) : undefined,
        error: error || undefined,
        results: results ? JSON.parse(results) : undefined,
      };
    } catch (error) {
      throw new Error(`Failed to get task status: ${error.message}`);
    }
  }

  async getAllParseTasks(): Promise<ParseTaskResponse[]> {
    try {
      // Get all task keys from Redis
      const taskKeys = await this.redisService.keys("task:*");
      const taskList: ParseTaskResponse[] = [];

      for (const key of taskKeys) {
        const taskId = key.replace("task:", "");
        try {
          const task = await this.getParseTaskStatus(taskId);
          // Convert ParseTaskStatus to ParseTaskResponse
          const taskResponse: ParseTaskResponse = {
            id: task.id,
            status: task.status,
            totalGroups: task.totalGroups,
            processedGroups: task.processedGroups,
            currentGroup: task.currentGroup,
            progress: task.progress,
            createdAt: task.createdAt || new Date(),
            completedAt: task.completedAt,
            error: task.error,
          };
          taskList.push(taskResponse);
        } catch (error) {
          this.logger.warn(`Error getting task ${taskId}:`, error);
          // Continue with other tasks
        }
      }

      return taskList.sort(
        (a, b) =>
          new Date(b.createdAt || new Date()).getTime() -
          new Date(a.createdAt || new Date()).getTime()
      );
    } catch (error) {
      this.logger.error("Error getting all tasks:", error);
      throw error;
    }
  }

  async cancelParseTask(taskId: string): Promise<{ message: string }> {
    try {
      // Update task status to cancelled
      const task = await this.getParseTaskStatus(taskId);
      task.status = "failed";
      task.error = "Task cancelled by user";

      await this.redisService.setTaskStatus(taskId, task);
      await this.redisService.setTaskError(taskId, "Task cancelled by user");
      await this.redisService.setTaskCompletedAt(taskId, new Date());

      return { message: "Task cancelled successfully" };
    } catch (error) {
      this.logger.error(`Error cancelling task ${taskId}:`, error);
      throw error;
    }
  }

  private async processParseTask(
    taskId: string,
    taskData: ParseTaskCreate
  ): Promise<void> {
    try {
      const maxConcurrent = 3;
      const queue = [...taskData.groupIds];
      let completed = 0;
      let running = 0;
      const totalGroups = queue.length;

      const updateTaskStatus = async (
        status: string,
        currentGroup?: string,
        progress?: number
      ) => {
        const task = await this.getParseTaskStatus(taskId);
        const updatedTask: ParseTaskResponse = {
          id: task.id,
          status: status as any,
          totalGroups: task.totalGroups,
          processedGroups: completed,
          currentGroup,
          progress: progress || Math.round((completed / totalGroups) * 100),
          createdAt: task.createdAt || new Date(),
          completedAt: task.completedAt,
          error: task.error,
        };

        if (status === "completed" || status === "failed") {
          updatedTask.completedAt = new Date();
        }

        await this.redisService.setTaskStatus(taskId, updatedTask);
        await this.redisService.setTaskProgress(taskId, updatedTask.progress);

        if (currentGroup) {
          await this.redisService.setCurrentGroup(taskId, currentGroup);
        }
      };

      const processNext = async () => {
        if (queue.length === 0 || running >= maxConcurrent) {
          return;
        }

        const groupId = queue.shift()!;
        running++;

        try {
          // Get group name
          const group = await this.getGroupById(groupId);
          await updateTaskStatus(
            "running",
            group.name,
            Math.round((completed / totalGroups) * 100)
          );

          // Parse group
          const result = await this.fullParseGroup(
            groupId,
            taskData.postsLimit,
            taskData.commentsLimit
          );

          completed++;
          running--;

          // Update processed groups count
          await this.redisService.incrementProcessedGroups(taskId);
          await this.redisService.incrementProcessedGroups(taskId);

          await updateTaskStatus(
            "running",
            group.name,
            Math.round((completed / totalGroups) * 100)
          );

          if (completed === totalGroups) {
            await updateTaskStatus("completed", undefined, 100);
            await this.redisService.setTaskCompletedAt(taskId, new Date());

            // Set results
            const results = {
              totalPosts: result.postsParsed,
              totalComments: result.commentsParsed,
              totalMatches: result.keywordsMatched,
            };
            await this.redisService.setTaskResults(taskId, results);
          } else {
            // Continue with next group after delay
            setTimeout(() => processNext(), 1000);
          }
        } catch (error) {
          this.logger.error(`Error processing group ${groupId}:`, error);
          completed++;
          running--;

          await this.redisService.setTaskError(taskId, error.message);

          if (completed === totalGroups) {
            await updateTaskStatus("failed", undefined, 100);
            await this.redisService.setTaskCompletedAt(taskId, new Date());
          } else {
            setTimeout(() => processNext(), 1000);
          }
        }

        // Start next group if possible
        if (running < maxConcurrent && queue.length > 0) {
          setTimeout(() => processNext(), 500);
        }
      };

      // Start processing
      await updateTaskStatus("running");
      for (let i = 0; i < Math.min(maxConcurrent, queue.length); i++) {
        setTimeout(() => processNext(), i * 500);
      }
    } catch (error) {
      this.logger.error(`Error processing task ${taskId}:`, error);
      // Handle error - task will be marked as failed in the main process
    }
  }
}
