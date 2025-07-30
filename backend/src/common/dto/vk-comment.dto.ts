import { ApiProperty } from "@nestjs/swagger";
import { IsString, IsNumber, IsOptional } from "class-validator";

export class CreateVKCommentDto {
  @ApiProperty({ description: "VK Comment ID" })
  @IsNumber()
  vkId: number;

  @ApiProperty({ description: "Post ID" })
  @IsString()
  postId: string;

  @ApiProperty({ description: "Comment text content" })
  @IsString()
  text: string;
}

export class UpdateVKCommentDto {
  @ApiProperty({ description: "Comment text content", required: false })
  @IsOptional()
  @IsString()
  text?: string;
}

export class VKCommentResponseDto {
  @ApiProperty({ description: "Comment ID" })
  id: string;

  @ApiProperty({ description: "VK Comment ID" })
  vkId: number;

  @ApiProperty({ description: "Post ID" })
  postId: string;

  @ApiProperty({ description: "Comment text content" })
  text: string;

  @ApiProperty({ description: "Comment creation date" })
  createdAt: Date;

  @ApiProperty({ description: "Comment last update date" })
  updatedAt: Date;
}
