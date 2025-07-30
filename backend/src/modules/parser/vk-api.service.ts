import { Injectable, Logger } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';

@Injectable()
export class VKApiService {
  private readonly logger = new Logger(VKApiService.name);
  private readonly baseUrl = 'https://api.vk.com/method';
  private readonly accessToken = process.env.VK_ACCESS_TOKEN;

  constructor(private readonly httpService: HttpService) {}

  async getGroupInfo(screenName: string) {
    try {
      const response = await firstValueFrom(
        this.httpService.get(`${this.baseUrl}/groups.getById`, {
          params: {
            group_id: screenName,
            access_token: this.accessToken,
            v: '5.131',
          },
        })
      );
      return response.data;
    } catch (error) {
      this.logger.error(`Error fetching group info for ${screenName}:`, error);
      throw error;
    }
  }

  async getGroupPosts(groupId: number, count: number = 100) {
    try {
      const response = await firstValueFrom(
        this.httpService.get(`${this.baseUrl}/wall.get`, {
          params: {
            owner_id: -groupId,
            count,
            access_token: this.accessToken,
            v: '5.131',
          },
        })
      );
      return response.data;
    } catch (error) {
      this.logger.error(`Error fetching posts for group ${groupId}:`, error);
      throw error;
    }
  }

  async getPostComments(ownerId: number, postId: number, count: number = 100) {
    try {
      const response = await firstValueFrom(
        this.httpService.get(`${this.baseUrl}/wall.getComments`, {
          params: {
            owner_id: ownerId,
            post_id: postId,
            count,
            access_token: this.accessToken,
            v: '5.131',
          },
        })
      );
      return response.data;
    } catch (error) {
      this.logger.error(`Error fetching comments for post ${postId}:`, error);
      throw error;
    }
  }
} 