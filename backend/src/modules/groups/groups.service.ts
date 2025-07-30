import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { VKGroup } from '@prisma/client';

@Injectable()
export class GroupsService {
  constructor(private prisma: PrismaService) {}

  async findAll(): Promise<VKGroup[]> {
    return this.prisma.vKGroup.findMany({
      where: { isActive: true },
      include: { posts: true },
    });
  }

  async findById(id: string): Promise<VKGroup | null> {
    return this.prisma.vKGroup.findUnique({
      where: { id },
      include: { posts: true },
    });
  }

  async findByVkId(vkId: number): Promise<VKGroup | null> {
    return this.prisma.vKGroup.findUnique({
      where: { vkId },
      include: { posts: true },
    });
  }

  async findByScreenName(screenName: string): Promise<VKGroup | null> {
    return this.prisma.vKGroup.findUnique({
      where: { screenName },
      include: { posts: true },
    });
  }

  async create(data: {
    vkId: number;
    screenName: string;
    name: string;
    description?: string;
  }): Promise<VKGroup> {
    return this.prisma.vKGroup.create({
      data,
    });
  }

  async update(id: string, data: Partial<VKGroup>): Promise<VKGroup> {
    return this.prisma.vKGroup.update({
      where: { id },
      data,
    });
  }

  async delete(id: string): Promise<VKGroup> {
    return this.prisma.vKGroup.update({
      where: { id },
      data: { isActive: false },
    });
  }
} 