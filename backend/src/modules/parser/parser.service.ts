import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { VKApiService } from './vk-api.service';
import { VKGroup, VKPost, VKComment } from '@prisma/client';

@Injectable()
export class ParserService {
  private readonly logger = new Logger(ParserService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly vkApiService: VKApiService,
  ) {}

  async parseGroup(screenName: string): Promise<VKGroup> {
    try {
      this.logger.log(`Starting to parse group: ${screenName}`);

      // Get group info from VK API
      const groupInfo = await this.vkApiService.getGroupInfo(screenName);
      
      if (!groupInfo.response || groupInfo.response.length === 0) {
        throw new Error(`Group not found: ${screenName}`);
      }

      const group = groupInfo.response[0];

      // Create or update group in database
      const existingGroup = await this.prisma.vKGroup.findUnique({
        where: { vkId: group.id },
      });

      if (existingGroup) {
        return this.prisma.vKGroup.update({
          where: { id: existingGroup.id },
          data: {
            name: group.name,
            screenName: group.screen_name,
            description: group.description,
          },
        });
      } else {
        return this.prisma.vKGroup.create({
          data: {
            vkId: group.id,
            screenName: group.screen_name,
            name: group.name,
            description: group.description,
          },
        });
      }
    } catch (error) {
      this.logger.error(`Error parsing group ${screenName}:`, error);
      throw error;
    }
  }

  async parseGroupPosts(groupId: string, limit: number = 100): Promise<VKPost[]> {
    try {
      this.logger.log(`Starting to parse posts for group: ${groupId}`);

      const group = await this.prisma.vKGroup.findUnique({
        where: { id: groupId },
      });

      if (!group) {
        throw new Error(`Group not found: ${groupId}`);
      }

      // Get posts from VK API
      const postsData = await this.vkApiService.getGroupPosts(group.vkId, limit);
      
      if (!postsData.response || !postsData.response.items) {
        this.logger.warn(`No posts found for group: ${groupId}`);
        return [];
      }

      const posts: VKPost[] = [];

      for (const post of postsData.response.items) {
        // Check if post already exists
        const existingPost = await this.prisma.vKPost.findUnique({
          where: { vkId: post.id },
        });

        if (!existingPost) {
          const createdPost = await this.prisma.vKPost.create({
            data: {
              vkId: post.id,
              groupId: group.id,
              text: post.text || '',
            },
          });
          posts.push(createdPost);
        }
      }

      this.logger.log(`Parsed ${posts.length} new posts for group: ${groupId}`);
      return posts;
    } catch (error) {
      this.logger.error(`Error parsing posts for group ${groupId}:`, error);
      throw error;
    }
  }

  async parsePostComments(postId: string, limit: number = 100): Promise<VKComment[]> {
    try {
      this.logger.log(`Starting to parse comments for post: ${postId}`);

      const post = await this.prisma.vKPost.findUnique({
        where: { id: postId },
        include: { group: true },
      });

      if (!post) {
        throw new Error(`Post not found: ${postId}`);
      }

      // Get comments from VK API
      const commentsData = await this.vkApiService.getPostComments(
        -post.group.vkId,
        post.vkId,
        limit
      );

      if (!commentsData.response || !commentsData.response.items) {
        this.logger.warn(`No comments found for post: ${postId}`);
        return [];
      }

      const comments: VKComment[] = [];

      for (const comment of commentsData.response.items) {
        // Check if comment already exists
        const existingComment = await this.prisma.vKComment.findUnique({
          where: { vkId: comment.id },
        });

        if (!existingComment) {
          const createdComment = await this.prisma.vKComment.create({
            data: {
              vkId: comment.id,
              postId: post.id,
              text: comment.text || '',
            },
          });
          comments.push(createdComment);
        }
      }

      this.logger.log(`Parsed ${comments.length} new comments for post: ${postId}`);
      return comments;
    } catch (error) {
      this.logger.error(`Error parsing comments for post ${postId}:`, error);
      throw error;
    }
  }
} 