import {
  Injectable,
  NotFoundException,
  ConflictException,
} from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service";
import { User } from "@prisma/client";
import {
  CreateUserDto,
  UpdateUserDto,
  UserResponseDto,
} from "../../common/dto";
import * as bcrypt from "bcrypt";

@Injectable()
export class UsersService {
  constructor(private prisma: PrismaService) {}

  async create(createUserDto: CreateUserDto): Promise<UserResponseDto> {
    // Check if user with this email already exists
    const existingUser = await this.prisma.user.findUnique({
      where: { email: createUserDto.email },
    });

    if (existingUser) {
      throw new ConflictException("User with this email already exists");
    }

    // Hash the password
    const hashedPassword = await bcrypt.hash(createUserDto.password, 10);

    const user = await this.prisma.user.create({
      data: {
        email: createUserDto.email,
        fullName: createUserDto.fullName,
        hashedPassword,
      },
    });

    return this.mapToResponseDto(user);
  }

  async findAll(): Promise<UserResponseDto[]> {
    const users = await this.prisma.user.findMany({
      orderBy: { createdAt: "desc" },
    });

    return users.map((user) => this.mapToResponseDto(user));
  }

  async findOne(id: string): Promise<UserResponseDto> {
    const user = await this.prisma.user.findUnique({
      where: { id },
    });

    if (!user) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }

    return this.mapToResponseDto(user);
  }

  async findByEmail(email: string): Promise<UserResponseDto | null> {
    const user = await this.prisma.user.findUnique({
      where: { email },
    });

    return user ? this.mapToResponseDto(user) : null;
  }

  async update(
    id: string,
    updateUserDto: UpdateUserDto
  ): Promise<UserResponseDto> {
    // Check if user exists
    const existingUser = await this.prisma.user.findUnique({
      where: { id },
    });

    if (!existingUser) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }

    // If email is being updated, check for conflicts
    if (updateUserDto.email && updateUserDto.email !== existingUser.email) {
      const emailConflict = await this.prisma.user.findUnique({
        where: { email: updateUserDto.email },
      });

      if (emailConflict) {
        throw new ConflictException("User with this email already exists");
      }
    }

    // Prepare update data
    const updateData: any = {};

    if (updateUserDto.email) updateData.email = updateUserDto.email;
    if (updateUserDto.fullName) updateData.fullName = updateUserDto.fullName;
    if (updateUserDto.isActive !== undefined)
      updateData.isActive = updateUserDto.isActive;

    // Hash password if provided
    if (updateUserDto.password) {
      updateData.hashedPassword = await bcrypt.hash(updateUserDto.password, 10);
    }

    const user = await this.prisma.user.update({
      where: { id },
      data: updateData,
    });

    return this.mapToResponseDto(user);
  }

  async remove(id: string): Promise<void> {
    const user = await this.prisma.user.findUnique({
      where: { id },
    });

    if (!user) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }

    await this.prisma.user.delete({
      where: { id },
    });
  }

  private mapToResponseDto(user: User): UserResponseDto {
    return {
      id: user.id,
      email: user.email,
      fullName: user.fullName,
      isActive: user.isActive,
      isSuperuser: user.isSuperuser,
      createdAt: user.createdAt,
      updatedAt: user.updatedAt,
    };
  }
}
