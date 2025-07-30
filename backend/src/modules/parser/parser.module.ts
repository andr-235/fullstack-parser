import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { ParserController } from './parser.controller';
import { ParserService } from './parser.service';
import { VKApiService } from './vk-api.service';

@Module({
  imports: [HttpModule],
  controllers: [ParserController],
  providers: [ParserService, VKApiService],
  exports: [ParserService, VKApiService],
})
export class ParserModule {} 