import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { Keyword } from '@prisma/client';

@Injectable()
export class KeywordsService {
  constructor(private prisma: PrismaService) {}

  async findAll(): Promise<Keyword[]> {
    return this.prisma.keyword.findMany({
      where: { isActive: true },
    });
  }

  async findById(id: string): Promise<Keyword | null> {
    return this.prisma.keyword.findUnique({
      where: { id },
    });
  }

  async findByWord(word: string): Promise<Keyword | null> {
    return this.prisma.keyword.findUnique({
      where: { word },
    });
  }

  async create(data: { word: string }): Promise<Keyword> {
    return this.prisma.keyword.create({
      data,
    });
  }

  async update(id: string, data: Partial<Keyword>): Promise<Keyword> {
    return this.prisma.keyword.update({
      where: { id },
      data,
    });
  }

  async delete(id: string): Promise<Keyword> {
    return this.prisma.keyword.update({
      where: { id },
      data: { isActive: false },
    });
  }

  async matchCommentsWithKeywords(commentIds: string[]): Promise<any[]> {
    return this.prisma.commentKeywordMatch.findMany({
      where: {
        commentId: { in: commentIds },
      },
      include: {
        comment: true,
        keyword: true,
      },
    });
  }
} 