import { ApiProperty } from "@nestjs/swagger";
import { IsString, IsNumber, IsOptional, IsBoolean } from "class-validator";

export class CreateVKGroupDto {
  @ApiProperty({ description: "VK Group ID" })
  @IsNumber()
  vkId: number;

  @ApiProperty({ description: "VK Group screen name" })
  @IsString()
  screenName: string;

  @ApiProperty({ description: "VK Group name" })
  @IsString()
  name: string;

  @ApiProperty({ description: "VK Group description", required: false })
  @IsOptional()
  @IsString()
  description?: string;
}

export class UpdateVKGroupDto {
  @ApiProperty({ description: "VK Group name", required: false })
  @IsOptional()
  @IsString()
  name?: string;

  @ApiProperty({ description: "VK Group description", required: false })
  @IsOptional()
  @IsString()
  description?: string;

  @ApiProperty({ description: "VK Group active status", required: false })
  @IsOptional()
  @IsBoolean()
  isActive?: boolean;
}

export class VKGroupResponseDto {
  @ApiProperty({ description: "Group ID" })
  id: string;

  @ApiProperty({ description: "VK Group ID" })
  vkId: number;

  @ApiProperty({ description: "VK Group screen name" })
  screenName: string;

  @ApiProperty({ description: "VK Group name" })
  name: string;

  @ApiProperty({ description: "VK Group description" })
  description: string;

  @ApiProperty({ description: "Group active status" })
  isActive: boolean;

  @ApiProperty({ description: "Group creation date" })
  createdAt: Date;

  @ApiProperty({ description: "Group last update date" })
  updatedAt: Date;

  @ApiProperty({ description: "Number of posts in the group" })
  postCount: number;
}
