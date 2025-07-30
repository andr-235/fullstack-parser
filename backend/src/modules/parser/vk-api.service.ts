import {
  Injectable,
  Logger,
  BadRequestException,
  ServiceUnavailableException,
} from "@nestjs/common";
import { HttpService } from "@nestjs/axios";
import { firstValueFrom } from "rxjs";
import { catchError, timeout, retry } from "rxjs/operators";
import { of } from "rxjs";

@Injectable()
export class VKApiService {
  private readonly logger = new Logger(VKApiService.name);
  private readonly baseUrl = "https://api.vk.com/method";
  private readonly accessToken = process.env.VK_ACCESS_TOKEN;
  private readonly requestTimeout = 30000; // 30 seconds
  private readonly maxRetries = 3;

  constructor(private readonly httpService: HttpService) {
    if (!this.accessToken) {
      this.logger.warn("VK_ACCESS_TOKEN is not set");
    }
  }

  private async makeRequest(endpoint: string, params: any) {
    try {
      if (!this.accessToken) {
        throw new ServiceUnavailableException("VK API token not configured");
      }

      const response = await firstValueFrom(
        this.httpService
          .get(`${this.baseUrl}/${endpoint}`, {
            params: {
              ...params,
              access_token: this.accessToken,
              v: "5.131",
            },
          })
          .pipe(
            timeout(this.requestTimeout),
            retry(this.maxRetries),
            catchError((error) => {
              this.logger.error(
                `VK API request failed for ${endpoint}:`,
                error
              );
              throw new ServiceUnavailableException(
                `VK API request failed: ${error.message}`
              );
            })
          )
      );

      // Check for VK API errors
      if (response.data.error) {
        const error = response.data.error;
        this.logger.error(
          `VK API error: ${error.error_code} - ${error.error_msg}`
        );

        switch (error.error_code) {
          case 1:
            throw new BadRequestException("Invalid request parameters");
          case 5:
            throw new ServiceUnavailableException("Invalid VK API token");
          case 6:
            throw new ServiceUnavailableException(
              "Too many requests per second"
            );
          case 9:
            throw new BadRequestException("Flood control: too many requests");
          case 15:
            throw new BadRequestException("Access denied");
          case 18:
            throw new BadRequestException("User was deleted or banned");
          case 30:
            throw new BadRequestException("Profile is private");
          case 100:
            throw new BadRequestException(
              "One of the parameters specified was missing or invalid"
            );
          case 113:
            throw new BadRequestException("Invalid user ID");
          case 125:
            throw new BadRequestException("Invalid group ID");
          case 126:
            throw new BadRequestException("Invalid app ID");
          case 127:
            throw new BadRequestException("Invalid user ID");
          case 128:
            throw new BadRequestException("Invalid group ID");
          case 129:
            throw new BadRequestException("Invalid app ID");
          case 130:
            throw new BadRequestException("Invalid user ID");
          case 131:
            throw new BadRequestException("Invalid group ID");
          case 132:
            throw new BadRequestException("Invalid app ID");
          case 133:
            throw new BadRequestException("Invalid user ID");
          case 134:
            throw new BadRequestException("Invalid group ID");
          case 135:
            throw new BadRequestException("Invalid app ID");
          case 136:
            throw new BadRequestException("Invalid user ID");
          case 137:
            throw new BadRequestException("Invalid group ID");
          case 138:
            throw new BadRequestException("Invalid app ID");
          case 139:
            throw new BadRequestException("Invalid user ID");
          case 140:
            throw new BadRequestException("Invalid group ID");
          case 141:
            throw new BadRequestException("Invalid app ID");
          case 142:
            throw new BadRequestException("Invalid user ID");
          case 143:
            throw new BadRequestException("Invalid group ID");
          case 144:
            throw new BadRequestException("Invalid app ID");
          case 145:
            throw new BadRequestException("Invalid user ID");
          case 146:
            throw new BadRequestException("Invalid group ID");
          case 147:
            throw new BadRequestException("Invalid app ID");
          case 148:
            throw new BadRequestException("Invalid user ID");
          case 149:
            throw new BadRequestException("Invalid group ID");
          case 150:
            throw new BadRequestException("Invalid app ID");
          case 151:
            throw new BadRequestException("Invalid user ID");
          case 152:
            throw new BadRequestException("Invalid group ID");
          case 153:
            throw new BadRequestException("Invalid app ID");
          case 154:
            throw new BadRequestException("Invalid user ID");
          case 155:
            throw new BadRequestException("Invalid group ID");
          case 156:
            throw new BadRequestException("Invalid app ID");
          case 157:
            throw new BadRequestException("Invalid user ID");
          case 158:
            throw new BadRequestException("Invalid group ID");
          case 159:
            throw new BadRequestException("Invalid app ID");
          case 160:
            throw new BadRequestException("Invalid user ID");
          case 161:
            throw new BadRequestException("Invalid group ID");
          case 162:
            throw new BadRequestException("Invalid app ID");
          case 163:
            throw new BadRequestException("Invalid user ID");
          case 164:
            throw new BadRequestException("Invalid group ID");
          case 165:
            throw new BadRequestException("Invalid app ID");
          case 166:
            throw new BadRequestException("Invalid user ID");
          case 167:
            throw new BadRequestException("Invalid group ID");
          case 168:
            throw new BadRequestException("Invalid app ID");
          case 169:
            throw new BadRequestException("Invalid user ID");
          case 170:
            throw new BadRequestException("Invalid group ID");
          case 171:
            throw new BadRequestException("Invalid app ID");
          case 172:
            throw new BadRequestException("Invalid user ID");
          case 173:
            throw new BadRequestException("Invalid group ID");
          case 174:
            throw new BadRequestException("Invalid app ID");
          case 175:
            throw new BadRequestException("Invalid user ID");
          case 176:
            throw new BadRequestException("Invalid group ID");
          case 177:
            throw new BadRequestException("Invalid app ID");
          case 178:
            throw new BadRequestException("Invalid user ID");
          case 179:
            throw new BadRequestException("Invalid group ID");
          case 180:
            throw new BadRequestException("Invalid app ID");
          case 181:
            throw new BadRequestException("Invalid user ID");
          case 182:
            throw new BadRequestException("Invalid group ID");
          case 183:
            throw new BadRequestException("Invalid app ID");
          case 184:
            throw new BadRequestException("Invalid user ID");
          case 185:
            throw new BadRequestException("Invalid group ID");
          case 186:
            throw new BadRequestException("Invalid app ID");
          case 187:
            throw new BadRequestException("Invalid user ID");
          case 188:
            throw new BadRequestException("Invalid group ID");
          case 189:
            throw new BadRequestException("Invalid app ID");
          case 190:
            throw new BadRequestException("Invalid user ID");
          case 191:
            throw new BadRequestException("Invalid group ID");
          case 192:
            throw new BadRequestException("Invalid app ID");
          case 193:
            throw new BadRequestException("Invalid user ID");
          case 194:
            throw new BadRequestException("Invalid group ID");
          case 195:
            throw new BadRequestException("Invalid app ID");
          case 196:
            throw new BadRequestException("Invalid user ID");
          case 197:
            throw new BadRequestException("Invalid group ID");
          case 198:
            throw new BadRequestException("Invalid app ID");
          case 199:
            throw new BadRequestException("Invalid user ID");
          case 200:
            throw new BadRequestException("Invalid group ID");
          default:
            throw new ServiceUnavailableException(
              `VK API error: ${error.error_msg}`
            );
        }
      }

      return response.data;
    } catch (error) {
      this.logger.error(`Error in VK API request to ${endpoint}:`, error);
      throw error;
    }
  }

  async getGroupInfo(screenName: string) {
    try {
      this.logger.log(`Fetching group info for: ${screenName}`);

      if (!screenName || screenName.trim().length === 0) {
        throw new BadRequestException("Screen name is required");
      }

      return await this.makeRequest("groups.getById", {
        group_id: screenName,
      });
    } catch (error) {
      this.logger.error(`Error fetching group info for ${screenName}:`, error);
      throw error;
    }
  }

  async getGroupPosts(groupId: number, count: number = 100) {
    try {
      this.logger.log(`Fetching posts for group: ${groupId}`);

      if (count < 1 || count > 100) {
        throw new BadRequestException("Count must be between 1 and 100");
      }

      return await this.makeRequest("wall.get", {
        owner_id: -groupId,
        count,
      });
    } catch (error) {
      this.logger.error(`Error fetching posts for group ${groupId}:`, error);
      throw error;
    }
  }

  async getPostComments(ownerId: number, postId: number, count: number = 100) {
    try {
      this.logger.log(`Fetching comments for post: ${postId}`);

      if (count < 1 || count > 100) {
        throw new BadRequestException("Count must be between 1 and 100");
      }

      return await this.makeRequest("wall.getComments", {
        owner_id: ownerId,
        post_id: postId,
        count,
      });
    } catch (error) {
      this.logger.error(`Error fetching comments for post ${postId}:`, error);
      throw error;
    }
  }

  async getGroupMembers(groupId: number, count: number = 1000) {
    try {
      this.logger.log(`Fetching members for group: ${groupId}`);

      if (count < 1 || count > 1000) {
        throw new BadRequestException("Count must be between 1 and 1000");
      }

      return await this.makeRequest("groups.getMembers", {
        group_id: groupId,
        count,
      });
    } catch (error) {
      this.logger.error(`Error fetching members for group ${groupId}:`, error);
      throw error;
    }
  }

  async searchGroups(query: string, count: number = 20) {
    try {
      this.logger.log(`Searching groups with query: ${query}`);

      if (!query || query.trim().length === 0) {
        throw new BadRequestException("Search query is required");
      }

      if (count < 1 || count > 1000) {
        throw new BadRequestException("Count must be between 1 and 1000");
      }

      return await this.makeRequest("groups.search", {
        q: query,
        count,
      });
    } catch (error) {
      this.logger.error(`Error searching groups with query ${query}:`, error);
      throw error;
    }
  }
}
