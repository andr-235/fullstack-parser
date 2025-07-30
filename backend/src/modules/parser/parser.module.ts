import { Module } from '@nestjs/common';
import { ParserController } from './parser.controller';
import { ParserService } from './parser.service';
import { VkApiService } from './vk-api.service';

@Module({
  controllers: [ParserController],
  providers: [ParserService, VkApiService],
  exports: [ParserService, VkApiService],
})
export class ParserModule {} 