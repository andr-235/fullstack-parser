-- CreateExtension
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- CreateEnum
CREATE TYPE "public"."GroupStatus" AS ENUM ('valid', 'invalid', 'duplicate');

-- CreateEnum
CREATE TYPE "public"."TaskStatus" AS ENUM ('pending', 'processing', 'completed', 'failed');

-- CreateEnum
CREATE TYPE "public"."TaskType" AS ENUM ('fetch_comments', 'process_groups', 'analyze_posts');

-- CreateTable
CREATE TABLE "public"."comments" (
    "id" SERIAL NOT NULL,
    "vk_comment_id" INTEGER NOT NULL,
    "post_vk_id" INTEGER NOT NULL,
    "owner_id" INTEGER NOT NULL,
    "author_id" INTEGER NOT NULL,
    "author_name" VARCHAR(255) NOT NULL,
    "text" TEXT NOT NULL DEFAULT '',
    "date" TIMESTAMP(3) NOT NULL,
    "likes" INTEGER NOT NULL DEFAULT 0,
    "userId" INTEGER,
    "postId" INTEGER,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "post_id" INTEGER,

    CONSTRAINT "comments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."groups" (
    "id" SERIAL NOT NULL,
    "name" TEXT,
    "task_id" UUID NOT NULL,
    "uploaded_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "status" "public"."GroupStatus" NOT NULL DEFAULT 'valid',

    CONSTRAINT "groups_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."posts" (
    "id" SERIAL NOT NULL,
    "vk_post_id" INTEGER NOT NULL,
    "owner_id" INTEGER NOT NULL,
    "group_id" INTEGER NOT NULL,
    "text" TEXT NOT NULL DEFAULT '',
    "date" TIMESTAMP(3) NOT NULL,
    "likes" INTEGER NOT NULL DEFAULT 0,
    "ownerId" INTEGER,
    "groupId" INTEGER,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "task_id" INTEGER NOT NULL,

    CONSTRAINT "posts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."tasks" (
    "id" SERIAL NOT NULL,
    "priority" SMALLINT NOT NULL DEFAULT 0,
    "progress" SMALLINT NOT NULL DEFAULT 0,
    "groups" JSONB,
    "metrics" JSONB,
    "parameters" JSONB,
    "result" JSONB,
    "error" TEXT,
    "executionTime" INTEGER,
    "startedAt" TIMESTAMP(3),
    "finishedAt" TIMESTAMP(3),
    "createdBy" VARCHAR(100) NOT NULL DEFAULT 'system',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "status" "public"."TaskStatus" NOT NULL DEFAULT 'pending',
    "type" "public"."TaskType" NOT NULL DEFAULT 'fetch_comments',

    CONSTRAINT "tasks_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "comments_vk_comment_id_key" ON "public"."comments"("vk_comment_id");

-- CreateIndex
CREATE INDEX "idx_comment_author" ON "public"."comments"("author_id");

-- CreateIndex
CREATE INDEX "idx_comment_date" ON "public"."comments"("date");

-- CreateIndex
CREATE INDEX "idx_comment_legacy_post" ON "public"."comments"("postId");

-- CreateIndex
CREATE INDEX "idx_comment_likes" ON "public"."comments"("likes");

-- CreateIndex
CREATE INDEX "idx_comment_owner" ON "public"."comments"("owner_id");

-- CreateIndex
CREATE INDEX "idx_comment_post" ON "public"."comments"("post_id");

-- CreateIndex
CREATE INDEX "idx_comment_post_vk" ON "public"."comments"("post_vk_id");

-- CreateIndex
CREATE INDEX "idx_comment_vk_id" ON "public"."comments"("vk_comment_id");

-- CreateIndex
CREATE INDEX "idx_group_name" ON "public"."groups"("name");

-- CreateIndex
CREATE INDEX "idx_group_status" ON "public"."groups"("status");

-- CreateIndex
CREATE INDEX "idx_group_task" ON "public"."groups"("task_id");

-- CreateIndex
CREATE INDEX "idx_group_uploaded" ON "public"."groups"("uploaded_at");

-- CreateIndex
CREATE UNIQUE INDEX "posts_vk_post_id_key" ON "public"."posts"("vk_post_id");

-- CreateIndex
CREATE INDEX "idx_post_date" ON "public"."posts"("date");

-- CreateIndex
CREATE INDEX "idx_post_group" ON "public"."posts"("group_id");

-- CreateIndex
CREATE INDEX "idx_post_likes" ON "public"."posts"("likes");

-- CreateIndex
CREATE INDEX "idx_post_owner" ON "public"."posts"("owner_id");

-- CreateIndex
CREATE INDEX "idx_post_task" ON "public"."posts"("task_id");

-- CreateIndex
CREATE INDEX "idx_post_vk_id" ON "public"."posts"("vk_post_id");

-- CreateIndex
CREATE INDEX "tasks_created_at" ON "public"."tasks"("createdAt");

-- CreateIndex
CREATE INDEX "tasks_status_idx" ON "public"."tasks"("status");

-- CreateIndex
CREATE INDEX "tasks_status_priority_idx" ON "public"."tasks"("status", "priority");

-- CreateIndex
CREATE INDEX "tasks_type_idx" ON "public"."tasks"("type");

-- CreateIndex
CREATE INDEX "tasks_type_status_idx" ON "public"."tasks"("type", "status");

-- AddForeignKey
ALTER TABLE "public"."comments" ADD CONSTRAINT "comments_postId_fkey" FOREIGN KEY ("postId") REFERENCES "public"."posts"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."comments" ADD CONSTRAINT "comments_post_id_fkey" FOREIGN KEY ("post_id") REFERENCES "public"."posts"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."posts" ADD CONSTRAINT "posts_task_id_fkey" FOREIGN KEY ("task_id") REFERENCES "public"."tasks"("id") ON DELETE CASCADE ON UPDATE CASCADE;
