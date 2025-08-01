import { ApiProperty } from "@nestjs/swagger";
import {
  IsArray,
  IsString,
  IsNumber,
  IsOptional,
  Min,
  Max,
} from "class-validator";

export class ParseTaskCreate {
  @ApiProperty({ description: "Group IDs to parse" })
  @IsArray()
  @IsString({ each: true })
  groupIds: string[];

  @ApiProperty({ description: "Posts limit per group", default: 100 })
  @IsOptional()
  @IsNumber()
  @Min(1)
  @Max(1000)
  postsLimit?: number = 100;

  @ApiProperty({ description: "Comments limit per post", default: 100 })
  @IsOptional()
  @IsNumber()
  @Min(1)
  @Max(1000)
  commentsLimit?: number = 100;
}

export class ParseTaskResponse {
  @ApiProperty({ description: "Task ID" })
  id: string;

  @ApiProperty({ description: "Task status" })
  status: "pending" | "running" | "completed" | "failed";

  @ApiProperty({ description: "Total groups to process" })
  totalGroups: number;

  @ApiProperty({ description: "Processed groups count" })
  processedGroups: number;

  @ApiProperty({ description: "Current group being processed" })
  currentGroup?: string;

  @ApiProperty({ description: "Progress percentage" })
  progress: number;

  @ApiProperty({ description: "Task creation time" })
  createdAt: Date;

  @ApiProperty({ description: "Task completion time" })
  completedAt?: Date;

  @ApiProperty({ description: "Error message if failed" })
  error?: string;
}

export class ParseTaskStatus {
  @ApiProperty({ description: "Task ID" })
  id: string;

  @ApiProperty({ description: "Task status" })
  status: "pending" | "running" | "completed" | "failed";

  @ApiProperty({ description: "Total groups to process" })
  totalGroups: number;

  @ApiProperty({ description: "Processed groups count" })
  processedGroups: number;

  @ApiProperty({ description: "Current group being processed" })
  currentGroup?: string;

  @ApiProperty({ description: "Progress percentage" })
  progress: number;

  @ApiProperty({ description: "Task creation time" })
  createdAt: Date;

  @ApiProperty({ description: "Task completion time" })
  completedAt?: Date;

  @ApiProperty({ description: "Error message if failed" })
  error?: string;

  @ApiProperty({ description: "Results summary" })
  results?: {
    totalPosts: number;
    totalComments: number;
    totalMatches: number;
  };
}
