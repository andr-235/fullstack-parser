import { Controller, Get, Post, Put, Delete, Body, Param, HttpCode, HttpStatus } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { KeywordsService } from './keywords.service';
import { Keyword } from '@prisma/client';

@ApiTags('keywords')
@Controller('keywords')
export class KeywordsController {
  constructor(private readonly keywordsService: KeywordsService) {}

  @Get()
  @ApiOperation({ summary: 'Get all keywords' })
  @ApiResponse({ status: 200, description: 'List of keywords' })
  async findAll(): Promise<Keyword[]> {
    return this.keywordsService.findAll();
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get keyword by ID' })
  @ApiResponse({ status: 200, description: 'Keyword found' })
  @ApiResponse({ status: 404, description: 'Keyword not found' })
  async findById(@Param('id') id: string): Promise<Keyword | null> {
    return this.keywordsService.findById(id);
  }

  @Post()
  @ApiOperation({ summary: 'Create new keyword' })
  @ApiResponse({ status: 201, description: 'Keyword created' })
  @ApiResponse({ status: 400, description: 'Bad request' })
  async create(@Body() data: { word: string }): Promise<Keyword> {
    return this.keywordsService.create(data);
  }

  @Put(':id')
  @ApiOperation({ summary: 'Update keyword' })
  @ApiResponse({ status: 200, description: 'Keyword updated' })
  @ApiResponse({ status: 404, description: 'Keyword not found' })
  async update(
    @Param('id') id: string,
    @Body() data: Partial<Keyword>,
  ): Promise<Keyword> {
    return this.keywordsService.update(id, data);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: 'Delete keyword' })
  @ApiResponse({ status: 204, description: 'Keyword deleted' })
  @ApiResponse({ status: 404, description: 'Keyword not found' })
  async delete(@Param('id') id: string): Promise<void> {
    await this.keywordsService.delete(id);
  }
} 