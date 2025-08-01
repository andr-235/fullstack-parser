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
  id: number;

  @ApiProperty({ description: "VK Comment ID" })
  vk_id: number;

  @ApiProperty({ description: "Group ID" })
  group_id: number;

  @ApiProperty({ description: "Group name" })
  group_name: string;

  @ApiProperty({ description: "Post ID" })
  post_id: number;

  @ApiProperty({ description: "Author ID" })
  author_id: number;

  @ApiProperty({ description: "Author name" })
  author_name: string;

  @ApiProperty({ description: "Author photo" })
  author_photo: string;

  @ApiProperty({ description: "Comment text content" })
  text: string;

  @ApiProperty({ description: "Comment date" })
  date: string;

  @ApiProperty({ description: "Likes count" })
  likes_count: number;

  @ApiProperty({ description: "Is viewed" })
  is_viewed: boolean;

  @ApiProperty({ description: "Is archived" })
  is_archived: boolean;

  @ApiProperty({ description: "Keywords found in comment", type: [String] })
  keywords: string[];

  @ApiProperty({ description: "Sentiment" })
  sentiment: "positive" | "negative" | "neutral";

  @ApiProperty({ description: "Comment creation date" })
  created_at: string;

  @ApiProperty({ description: "Comment last update date" })
  updated_at: string;
}
