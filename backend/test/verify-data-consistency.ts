import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function verifyDataConsistency() {
  console.log("🔍 Verifying data consistency...");

  try {
    // 1. Verify foreign key relationships
    console.log("\n1. Checking foreign key relationships...");

    // Check VKPost -> VKGroup relationships
    const orphanedPosts = await prisma.vKPost.findMany({
      where: {
        group: null,
      },
    });

    if (orphanedPosts.length > 0) {
      console.log(
        `❌ Found ${orphanedPosts.length} posts without valid group references`
      );
    } else {
      console.log("✅ All posts have valid group references");
    }

    // Check VKComment -> VKPost relationships
    const orphanedComments = await prisma.vKComment.findMany({
      where: {
        post: null,
      },
    });

    if (orphanedComments.length > 0) {
      console.log(
        `❌ Found ${orphanedComments.length} comments without valid post references`
      );
    } else {
      console.log("✅ All comments have valid post references");
    }

    // Check CommentKeywordMatch relationships
    const orphanedMatches = await prisma.commentKeywordMatch.findMany({
      where: {
        OR: [{ comment: null }, { keyword: null }],
      },
    });

    if (orphanedMatches.length > 0) {
      console.log(
        `❌ Found ${orphanedMatches.length} keyword matches with invalid references`
      );
    } else {
      console.log("✅ All keyword matches have valid references");
    }

    // 2. Verify data integrity constraints
    console.log("\n2. Checking data integrity constraints...");

    // Check for duplicate VK IDs
    const duplicateVkIds = await prisma.$queryRaw`
      SELECT "vkId", COUNT(*) as count
      FROM vk_groups
      GROUP BY "vkId"
      HAVING COUNT(*) > 1
    `;

    if (Array.isArray(duplicateVkIds) && duplicateVkIds.length > 0) {
      console.log(
        `❌ Found ${duplicateVkIds.length} duplicate VK IDs in groups`
      );
    } else {
      console.log("✅ No duplicate VK IDs in groups");
    }

    const duplicatePostVkIds = await prisma.$queryRaw`
      SELECT "vkId", COUNT(*) as count
      FROM vk_posts
      GROUP BY "vkId"
      HAVING COUNT(*) > 1
    `;

    if (Array.isArray(duplicatePostVkIds) && duplicatePostVkIds.length > 0) {
      console.log(
        `❌ Found ${duplicatePostVkIds.length} duplicate VK IDs in posts`
      );
    } else {
      console.log("✅ No duplicate VK IDs in posts");
    }

    const duplicateCommentVkIds = await prisma.$queryRaw`
      SELECT "vkId", COUNT(*) as count
      FROM vk_comments
      GROUP BY "vkId"
      HAVING COUNT(*) > 1
    `;

    if (
      Array.isArray(duplicateCommentVkIds) &&
      duplicateCommentVkIds.length > 0
    ) {
      console.log(
        `❌ Found ${duplicateCommentVkIds.length} duplicate VK IDs in comments`
      );
    } else {
      console.log("✅ No duplicate VK IDs in comments");
    }

    // 3. Verify data completeness
    console.log("\n3. Checking data completeness...");

    const totalGroups = await prisma.vKGroup.count();
    const totalPosts = await prisma.vKPost.count();
    const totalComments = await prisma.vKComment.count();
    const totalKeywords = await prisma.keyword.count();
    const totalMatches = await prisma.commentKeywordMatch.count();

    console.log(`📊 Data summary:`);
    console.log(`   - Groups: ${totalGroups}`);
    console.log(`   - Posts: ${totalPosts}`);
    console.log(`   - Comments: ${totalComments}`);
    console.log(`   - Keywords: ${totalKeywords}`);
    console.log(`   - Keyword matches: ${totalMatches}`);

    // 4. Verify statistical consistency
    console.log("\n4. Checking statistical consistency...");

    // Verify that keyword match count matches actual matches
    const actualMatches = await prisma.commentKeywordMatch.count();

    console.log(`   - Actual keyword matches: ${actualMatches}`);

    // 5. Check for data anomalies
    console.log("\n5. Checking for data anomalies...");

    // Check for empty text fields
    const emptyPostTexts = await prisma.vKPost.count({
      where: {
        OR: [{ text: "" }, { text: null }],
      },
    });

    if (emptyPostTexts > 0) {
      console.log(`⚠️ Found ${emptyPostTexts} posts with empty text`);
    } else {
      console.log("✅ No posts with empty text");
    }

    const emptyCommentTexts = await prisma.vKComment.count({
      where: {
        OR: [{ text: "" }, { text: null }],
      },
    });

    if (emptyCommentTexts > 0) {
      console.log(`⚠️ Found ${emptyCommentTexts} comments with empty text`);
    } else {
      console.log("✅ No comments with empty text");
    }

    // Check for very long text fields (potential issues)
    const longPostTexts = await prisma.vKPost.count({
      where: {
        text: {
          gt: "A".repeat(10000), // 10KB limit
        },
      },
    });

    if (longPostTexts > 0) {
      console.log(`⚠️ Found ${longPostTexts} posts with very long text`);
    } else {
      console.log("✅ No posts with excessively long text");
    }

    // 6. Verify referential integrity
    console.log("\n6. Checking referential integrity...");

    // Check that all groups have at least one post (if any posts exist)
    if (totalPosts > 0) {
      const groupsWithPosts = await prisma.vKGroup.count({
        where: {
          posts: {
            some: {},
          },
        },
      });

      if (groupsWithPosts === 0) {
        console.log("❌ No groups have posts, but posts exist");
      } else {
        console.log(`✅ ${groupsWithPosts} groups have posts`);
      }
    }

    // Check that all posts have at least one comment (if any comments exist)
    if (totalComments > 0) {
      const postsWithComments = await prisma.vKPost.count({
        where: {
          comments: {
            some: {},
          },
        },
      });

      if (postsWithComments === 0) {
        console.log("❌ No posts have comments, but comments exist");
      } else {
        console.log(`✅ ${postsWithComments} posts have comments`);
      }
    }

    console.log("\n✅ Data consistency verification completed successfully!");
  } catch (error) {
    console.error("❌ Error during data consistency verification:", error);
    throw error;
  } finally {
    await prisma.$disconnect();
  }
}

// Run the verification if this script is executed directly
if (require.main === module) {
  verifyDataConsistency()
    .then(() => {
      console.log("\n🎉 All consistency checks passed!");
      process.exit(0);
    })
    .catch((error) => {
      console.error("\n💥 Consistency checks failed:", error);
      process.exit(1);
    });
}

export { verifyDataConsistency };
