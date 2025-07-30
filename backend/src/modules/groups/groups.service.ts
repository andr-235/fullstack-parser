import {
  Injectable,
  NotFoundException,
  ConflictException,
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
    // Check if group with this VK ID already exists
    const existingGroup = await this.prisma.vKGroup.findUnique({
      where: { vkId: createGroupDto.vkId },
    });

    if (existingGroup) {
      throw new ConflictException("Group with this VK ID already exists");
    }

    // Check if group with this screen name already exists
    const existingScreenName = await this.prisma.vKGroup.findUnique({
      where: { screenName: createGroupDto.screenName },
    });

    if (existingScreenName) {
      throw new ConflictException("Group with this screen name already exists");
    }

    const group = await this.prisma.vKGroup.create({
      data: {
        vkId: createGroupDto.vkId,
        screenName: createGroupDto.screenName,
        name: createGroupDto.name,
        description: createGroupDto.description,
      },
    });

    return this.mapToResponseDto(group);
  }

  async findAll(): Promise<VKGroupResponseDto[]> {
    const groups = await this.prisma.vKGroup.findMany({
      orderBy: { createdAt: "desc" },
    });

    return groups.map((group) => this.mapToResponseDto(group));
  }

  async findOne(id: string): Promise<VKGroupResponseDto> {
    const group = await this.prisma.vKGroup.findUnique({
      where: { id },
    });

    if (!group) {
      throw new NotFoundException(`Group with ID ${id} not found`);
    }

    return this.mapToResponseDto(group);
  }

  async findByVkId(vkId: number): Promise<VKGroupResponseDto | null> {
    const group = await this.prisma.vKGroup.findUnique({
      where: { vkId },
    });

    return group ? this.mapToResponseDto(group) : null;
  }

  async findByScreenName(
    screenName: string
  ): Promise<VKGroupResponseDto | null> {
    const group = await this.prisma.vKGroup.findUnique({
      where: { screenName },
    });

    return group ? this.mapToResponseDto(group) : null;
  }

  async update(
    id: string,
    updateGroupDto: UpdateVKGroupDto
  ): Promise<VKGroupResponseDto> {
    // Check if group exists
    const existingGroup = await this.prisma.vKGroup.findUnique({
      where: { id },
    });

    if (!existingGroup) {
      throw new NotFoundException(`Group with ID ${id} not found`);
    }

    // Prepare update data
    const updateData: any = {};

    if (updateGroupDto.name) updateData.name = updateGroupDto.name;
    if (updateGroupDto.description !== undefined)
      updateData.description = updateGroupDto.description;
    if (updateGroupDto.isActive !== undefined)
      updateData.isActive = updateGroupDto.isActive;

    const group = await this.prisma.vKGroup.update({
      where: { id },
      data: updateData,
    });

    return this.mapToResponseDto(group);
  }

  async remove(id: string): Promise<void> {
    const group = await this.prisma.vKGroup.findUnique({
      where: { id },
    });

    if (!group) {
      throw new NotFoundException(`Group with ID ${id} not found`);
    }

    await this.prisma.vKGroup.delete({
      where: { id },
    });
  }

  private mapToResponseDto(group: VKGroup): VKGroupResponseDto {
    return {
      id: group.id,
      vkId: group.vkId,
      screenName: group.screenName,
      name: group.name,
      description: group.description,
      isActive: group.isActive,
      createdAt: group.createdAt,
      updatedAt: group.updatedAt,
    };
  }
}
