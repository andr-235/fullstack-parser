import {
  Controller,
  Get,
  Post,
  Body,
  Patch,
  Param,
  Delete,
  HttpCode,
  HttpStatus,
} from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse, ApiParam } from "@nestjs/swagger";
import { UsersService } from "./users.service";
import {
  CreateUserDto,
  UpdateUserDto,
  UserResponseDto,
} from "../../common/dto";

@ApiTags("users")
@Controller("users")
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Post()
  @ApiOperation({ summary: "Create a new user" })
  @ApiResponse({
    status: 201,
    description: "User created successfully",
    type: UserResponseDto,
  })
  @ApiResponse({
    status: 409,
    description: "User with this email already exists",
  })
  async create(@Body() createUserDto: CreateUserDto): Promise<UserResponseDto> {
    return this.usersService.create(createUserDto);
  }

  @Get()
  @ApiOperation({ summary: "Get all users" })
  @ApiResponse({
    status: 200,
    description: "List of all users",
    type: [UserResponseDto],
  })
  async findAll(): Promise<UserResponseDto[]> {
    return this.usersService.findAll();
  }

  @Get(":id")
  @ApiOperation({ summary: "Get user by ID" })
  @ApiParam({ name: "id", description: "User ID" })
  @ApiResponse({
    status: 200,
    description: "User found",
    type: UserResponseDto,
  })
  @ApiResponse({
    status: 404,
    description: "User not found",
  })
  async findOne(@Param("id") id: string): Promise<UserResponseDto> {
    return this.usersService.findOne(id);
  }

  @Patch(":id")
  @ApiOperation({ summary: "Update user by ID" })
  @ApiParam({ name: "id", description: "User ID" })
  @ApiResponse({
    status: 200,
    description: "User updated successfully",
    type: UserResponseDto,
  })
  @ApiResponse({
    status: 404,
    description: "User not found",
  })
  @ApiResponse({
    status: 409,
    description: "User with this email already exists",
  })
  async update(
    @Param("id") id: string,
    @Body() updateUserDto: UpdateUserDto
  ): Promise<UserResponseDto> {
    return this.usersService.update(id, updateUserDto);
  }

  @Delete(":id")
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: "Delete user by ID" })
  @ApiParam({ name: "id", description: "User ID" })
  @ApiResponse({
    status: 204,
    description: "User deleted successfully",
  })
  @ApiResponse({
    status: 404,
    description: "User not found",
  })
  async remove(@Param("id") id: string): Promise<void> {
    return this.usersService.remove(id);
  }
}
