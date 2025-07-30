import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { VKComment } from '@prisma/client';

@Injectable()
export class CommentsService {
  constructor(private prisma: PrismaService) {}

  async findAll(): Promise<VKComment[]> {
    return this.prisma.vKComment.findMany({
      include: { post: true },
    });
  }

  async findById(id: string): Promise<VKComment | null> {
    return this.prisma.vKComment.findUnique({
      where: { id },
      include: { post: true },
    });
  }

  async findByPostId(postId: string): Promise<VKComment[]> {
    return this.prisma.vKComment.findMany({
      where: { postId },
      include: { post: true },
    });
  }

  async findByVkId(vkId: number): Promise<VKComment | null> {
    return this.prisma.vKComment.findUnique({
      where: { vkId },
      include: { post: true },
    });
  }

  async create(data: {
    vkId: number;
    postId: string;
    text: string;
  }): Promise<VKComment> {
    return this.prisma.vKComment.create({
      data,
      include: { post: true },
    });
  }

  async update(id: string, data: Partial<VKComment>): Promise<VKComment> {
    return this.prisma.vKComment.update({
      where: { id },
      data,
      include: { post: true },
    });
  }

  async delete(id: string): Promise<VKComment> {
    return this.prisma.vKComment.update({
      where: { id },
      data: { text: '[DELETED]' },
      include: { post: true },
    });
  }

  async searchByText(text: string): Promise<VKComment[]> {
    return this.prisma.vKComment.findMany({
      where: {
        text: {
          contains: text,
          mode: 'insensitive',
        },
      },
      include: { post: true },
    });
  }
} 