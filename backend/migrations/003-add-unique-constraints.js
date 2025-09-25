module.exports = {
  up: async (queryInterface, Sequelize) => {
    // Add unique constraints to VK ID fields
    // Note: This migration assumes data has been properly migrated and no duplicates exist

    try {
      // Add unique constraint on vk_post_id (only for non-null values)
      await queryInterface.addConstraint('posts', {
        fields: ['vk_post_id'],
        type: 'unique',
        name: 'posts_vk_post_id_unique'
      });
    } catch (error) {
      console.log('Warning: Could not add unique constraint to vk_post_id, may already exist or have duplicate data');
    }

    try {
      // Add unique constraint on vk_comment_id (only for non-null values)
      await queryInterface.addConstraint('comments', {
        fields: ['vk_comment_id'],
        type: 'unique',
        name: 'comments_vk_comment_id_unique'
      });
    } catch (error) {
      console.log('Warning: Could not add unique constraint to vk_comment_id, may already exist or have duplicate data');
    }

    // Add indexes for better query performance
    await queryInterface.addIndex('posts', ['group_id'], {
      name: 'posts_group_id_index'
    });

    await queryInterface.addIndex('posts', ['owner_id'], {
      name: 'posts_owner_id_index'
    });

    await queryInterface.addIndex('comments', ['post_vk_id'], {
      name: 'comments_post_vk_id_index'
    });

    await queryInterface.addIndex('comments', ['author_id'], {
      name: 'comments_author_id_index'
    });
  },

  down: async (queryInterface, Sequelize) => {
    // Remove constraints and indexes
    await queryInterface.removeConstraint('posts', 'posts_vk_post_id_unique');
    await queryInterface.removeConstraint('comments', 'comments_vk_comment_id_unique');

    await queryInterface.removeIndex('posts', 'posts_group_id_index');
    await queryInterface.removeIndex('posts', 'posts_owner_id_index');
    await queryInterface.removeIndex('comments', 'comments_post_vk_id_index');
    await queryInterface.removeIndex('comments', 'comments_author_id_index');
  }
};