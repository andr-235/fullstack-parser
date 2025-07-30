import { ApiProperty } from "@nestjs/swagger";
import { IsString, IsOptional, IsBoolean } from "class-validator";

export class CreateKeywordDto {
  @ApiProperty({ description: "Keyword word" })
  @IsString()
  word: string;

  @ApiProperty({ description: "Keyword active status", required: false })
  @IsOptional()
  @IsBoolean()
  isActive?: boolean;
}

export class UpdateKeywordDto {
  @ApiProperty({ description: "Keyword word", required: false })
  @IsOptional()
  @IsString()
  word?: string;

  @ApiProperty({ description: "Keyword active status", required: false })
  @IsOptional()
  @IsBoolean()
  isActive?: boolean;
}

export class KeywordResponseDto {
  @ApiProperty({ description: "Keyword ID" })
  id: string;

  @ApiProperty({ description: "Keyword word" })
  word: string;

  @ApiProperty({ description: "Keyword active status" })
  isActive: boolean;

  @ApiProperty({ description: "Keyword creation date" })
  createdAt: Date;

  @ApiProperty({ description: "Keyword last update date" })
  updatedAt: Date;
}
