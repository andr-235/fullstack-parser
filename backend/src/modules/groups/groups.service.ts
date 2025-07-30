import {
  Injectable,
  NotFoundException,
  ConflictException,
  BadRequestException,
} from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service";
import { VKGroup } from "@prisma/client";
import {
  CreateVKGroupDto,
  UpdateVKGroupDto,
  VKGroupResponseDto,
} from "../../common/dto";

@Injectable()
export class GroupsService {
  constructor(private prisma: PrismaService) {}

  async create(createGroupDto: CreateVKGroupDto): Promise<VKGroupResponseDto> {
    // Check if group already exists by vkId
    const existingGroup = await this.prisma.vKGroup.findUnique({
      where: { vkId: createGroupDto.vkId },
    });

    if (existingGroup) {
      throw new ConflictException("Group with this VK ID already exists");
    }

    // Check if screen name is already taken
    const existingScreenName = await this.prisma.vKGroup.findUnique({
      where: { screenName: createGroupDto.screenName },
    });

    if (existingScreenName) {
      throw new ConflictException("Group with this screen name already exists");
    }

    const group = await this.prisma.vKGroup.create({
      data: createGroupDto,
    });

    return this.mapToResponseDto(group);
  }

  async findAll(
    page: number = 1,
    limit: number = 20,
    search?: string,
    isActive?: boolean
  ): Promise<{
    groups: VKGroupResponseDto[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    const skip = (page - 1) * limit;

    // Build where clause
    const where: any = {};

    if (search) {
      where.OR = [
        { name: { contains: search, mode: "insensitive" } },
        { screenName: { contains: search, mode: "insensitive" } },
        { description: { contains: search, mode: "insensitive" } },
      ];
    }

    if (isActive !== undefined) {
      where.isActive = isActive;
    }

    const [groups, total] = await Promise.all([
      this.prisma.vKGroup.findMany({
        where,
        skip,
        take: limit,
        include: {
          _count: {
            select: {
              posts: true,
            },
          },
        },
        orderBy: {
          createdAt: "desc",
        },
      }),
      this.prisma.vKGroup.count({ where }),
    ]);

    const totalPages = Math.ceil(total / limit);

    return {
      groups: groups.map((group) => this.mapToResponseDto(group)),
      total,
      page,
      limit,
      totalPages,
    };
  }

  async findOne(id: string): Promise<VKGroupResponseDto> {
    const group = await this.prisma.vKGroup.findUnique({
      where: { id: parseInt(id) },
      include: {
        _count: {
          select: {
            posts: true,
          },
        },
      },
    });

    if (!group) {
      throw new NotFoundException(`Group with ID ${id} not found`);
    }

    return this.mapToResponseDto(group);
  }

  async findByVkId(vkId: number): Promise<VKGroupResponseDto> {
    const group = await this.prisma.vKGroup.findUnique({
      where: { vkId },
      include: {
        _count: {
          select: {
            posts: true,
          },
        },
      },
    });

    if (!group) {
      throw new NotFoundException(`Group with VK ID ${vkId} not found`);
    }

    return this.mapToResponseDto(group);
  }

  async findByScreenName(screenName: string): Promise<VKGroupResponseDto> {
    const group = await this.prisma.vKGroup.findUnique({
      where: { screenName },
      include: {
        _count: {
          select: {
            posts: true,
          },
        },
      },
    });

    if (!group) {
      throw new NotFoundException(
        `Group with screen name ${screenName} not found`
      );
    }

    return this.mapToResponseDto(group);
  }

  async update(
    id: string,
    updateGroupDto: UpdateVKGroupDto
  ): Promise<VKGroupResponseDto> {
    // Check if group exists
    const existingGroup = await this.prisma.vKGroup.findUnique({
      where: { id: parseInt(id) },
    });

    if (!existingGroup) {
      throw new NotFoundException(`Group with ID ${id} not found`);
    }

    const group = await this.prisma.vKGroup.update({
      where: { id: parseInt(id) },
      data: updateGroupDto,
      include: {
        _count: {
          select: {
            posts: true,
          },
        },
      },
    });

    return this.mapToResponseDto(group);
  }

  async remove(id: string): Promise<void> {
    const group = await this.prisma.vKGroup.findUnique({
      where: { id: parseInt(id) },
    });

    if (!group) {
      throw new NotFoundException(`Group with ID ${id} not found`);
    }

    await this.prisma.vKGroup.delete({
      where: { id: parseInt(id) },
    });
  }

  async getStatistics() {
    const [
      totalGroups,
      activeGroups,
      inactiveGroups,
      groupsWithPosts,
      topGroups,
    ] = await Promise.all([
      this.prisma.vKGroup.count(),
      this.prisma.vKGroup.count({
        where: { isActive: true },
      }),
      this.prisma.vKGroup.count({
        where: { isActive: false },
      }),
      this.prisma.vKGroup.count({
        where: {
          posts: {
            some: {},
          },
        },
      }),
      this.prisma.vKGroup.findMany({
        include: {
          _count: {
            select: {
              posts: true,
            },
          },
        },
        orderBy: {
          posts: {
            _count: "desc",
          },
        },
        take: 10,
      }),
    ]);

    // Calculate average posts per group
    const totalPosts = topGroups.reduce(
      (sum, group) => sum + group._count.posts,
      0
    );
    const averagePostsPerGroup = totalGroups > 0 ? totalPosts / totalGroups : 0;

    return {
      totalGroups,
      activeGroups,
      inactiveGroups,
      groupsWithPosts,
      averagePostsPerGroup,
      topGroups: topGroups.map((group) => ({
        id: group.id,
        vkId: group.vkId,
        screenName: group.screenName,
        name: group.name,
        postCount: group._count.posts,
      })),
    };
  }

  async bulkUpdateStatus(ids: string[], isActive: boolean): Promise<number> {
    const numericIds = ids.map((id) => parseInt(id));

    const result = await this.prisma.vKGroup.updateMany({
      where: {
        id: {
          in: numericIds,
        },
      },
      data: {
        isActive,
      },
    });

    return result.count;
  }

  async searchGroups(
    query: string,
    limit: number = 20
  ): Promise<VKGroupResponseDto[]> {
    if (!query || query.trim().length === 0) {
      throw new BadRequestException("Search query is required");
    }

    if (limit < 1 || limit > 100) {
      throw new BadRequestException("Limit must be between 1 and 100");
    }

    const groups = await this.prisma.vKGroup.findMany({
      where: {
        OR: [
          { name: { contains: query, mode: "insensitive" } },
          { screenName: { contains: query, mode: "insensitive" } },
          { description: { contains: query, mode: "insensitive" } },
        ],
      },
      include: {
        _count: {
          select: {
            posts: true,
          },
        },
      },
      take: limit,
      orderBy: {
        createdAt: "desc",
      },
    });

    return groups.map((group) => this.mapToResponseDto(group));
  }

  async getGroupsByPostCount(
    minPosts: number = 1
  ): Promise<VKGroupResponseDto[]> {
    const groups = await this.prisma.vKGroup.findMany({
      where: {
        posts: {
          some: {},
        },
      },
      include: {
        _count: {
          select: {
            posts: true,
          },
        },
      },
      orderBy: {
        posts: {
          _count: "desc",
        },
      },
    });

    // Filter by minimum post count
    return groups
      .filter((group) => group._count.posts >= minPosts)
      .map((group) => this.mapToResponseDto(group));
  }

  private mapToResponseDto(group: any): VKGroupResponseDto {
    return {
      id: group.id,
      vkId: group.vkId,
      screenName: group.screenName,
      name: group.name,
      description: group.description,
      isActive: group.isActive,
      createdAt: group.createdAt,
      updatedAt: group.updatedAt,
      postCount: group._count?.posts || 0,
    };
  }
}
