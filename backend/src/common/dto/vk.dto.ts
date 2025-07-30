import { ApiProperty } from "@nestjs/swagger";

export class VKGroupDto {
  @ApiProperty({ description: "Group ID" })
  id: string;

  @ApiProperty({ description: "Group VK ID" })
  vkId: number;

  @ApiProperty({ description: "Group screen name" })
  screenName: string;

  @ApiProperty({ description: "Group name" })
  name: string;

  @ApiProperty({ description: "Group description", required: false })
  description?: string;

  @ApiProperty({ description: "Group active status" })
  isActive: boolean;

  @ApiProperty({ description: "Group creation date" })
  createdAt: Date;

  @ApiProperty({ description: "Group last update date" })
  updatedAt: Date;
}

export class VKPostDto {
  @ApiProperty({ description: "Post ID" })
  id: string;

  @ApiProperty({ description: "Post VK ID" })
  vkId: number;

  @ApiProperty({ description: "Post text" })
  text: string;

  @ApiProperty({ description: "Post creation date" })
  createdAt: Date;

  @ApiProperty({ description: "Post last update date" })
  updatedAt: Date;

  @ApiProperty({ description: "Group ID" })
  groupId: string;
}

export class VKCommentDto {
  @ApiProperty({ description: "Comment ID" })
  id: string;

  @ApiProperty({ description: "Comment VK ID" })
  vkId: number;

  @ApiProperty({ description: "Comment text" })
  text: string;

  @ApiProperty({ description: "Comment creation date" })
  createdAt: Date;

  @ApiProperty({ description: "Comment last update date" })
  updatedAt: Date;

  @ApiProperty({ description: "Post ID" })
  postId: string;
}
