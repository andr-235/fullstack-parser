import { ApiProperty } from "@nestjs/swagger";
import { IsEmail, IsString, IsOptional, IsBoolean } from "class-validator";

export class CreateUserDto {
  @ApiProperty({ description: "User email address" })
  @IsEmail()
  email: string;

  @ApiProperty({ description: "User full name" })
  @IsString()
  fullName: string;

  @ApiProperty({ description: "User password" })
  @IsString()
  password: string;
}

export class UpdateUserDto {
  @ApiProperty({ description: "User email address", required: false })
  @IsOptional()
  @IsEmail()
  email?: string;

  @ApiProperty({ description: "User full name", required: false })
  @IsOptional()
  @IsString()
  fullName?: string;

  @ApiProperty({ description: "User password", required: false })
  @IsOptional()
  @IsString()
  password?: string;

  @ApiProperty({ description: "User active status", required: false })
  @IsOptional()
  @IsBoolean()
  isActive?: boolean;
}

export class UserResponseDto {
  @ApiProperty({ description: "User ID" })
  id: string;

  @ApiProperty({ description: "User email address" })
  email: string;

  @ApiProperty({ description: "User full name" })
  fullName: string;

  @ApiProperty({ description: "User active status" })
  isActive: boolean;

  @ApiProperty({ description: "User superuser status" })
  isSuperuser: boolean;

  @ApiProperty({ description: "User creation date" })
  createdAt: Date;

  @ApiProperty({ description: "User last update date" })
  updatedAt: Date;
}
