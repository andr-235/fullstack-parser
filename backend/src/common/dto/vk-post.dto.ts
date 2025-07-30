import { ApiProperty } from "@nestjs/swagger";
import { IsString, IsNumber, IsOptional } from "class-validator";

export class CreateVKPostDto {
  @ApiProperty({ description: "VK Post ID" })
  @IsNumber()
  vkId: number;

  @ApiProperty({ description: "Group ID" })
  @IsString()
  groupId: string;

  @ApiProperty({ description: "Post text content" })
  @IsString()
  text: string;
}

export class UpdateVKPostDto {
  @ApiProperty({ description: "Post text content", required: false })
  @IsOptional()
  @IsString()
  text?: string;
}

export class VKPostResponseDto {
  @ApiProperty({ description: "Post ID" })
  id: string;

  @ApiProperty({ description: "VK Post ID" })
  vkId: number;

  @ApiProperty({ description: "Group ID" })
  groupId: string;

  @ApiProperty({ description: "Post text content" })
  text: string;

  @ApiProperty({ description: "Post creation date" })
  createdAt: Date;

  @ApiProperty({ description: "Post last update date" })
  updatedAt: Date;
}
