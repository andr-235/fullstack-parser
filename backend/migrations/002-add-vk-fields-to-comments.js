module.exports = {
  up: async (queryInterface, Sequelize) => {
    // Add new VK-specific fields to comments table
    await queryInterface.addColumn('comments', 'vk_comment_id', {
      type: Sequelize.INTEGER,
      allowNull: true, // Allow null initially for existing records
    });

    await queryInterface.addColumn('comments', 'post_vk_id', {
      type: Sequelize.INTEGER,
      allowNull: true, // Allow null initially for existing records
    });

    await queryInterface.addColumn('comments', 'owner_id', {
      type: Sequelize.INTEGER,
      allowNull: true, // Allow null initially for existing records
    });

    await queryInterface.addColumn('comments', 'author_id', {
      type: Sequelize.INTEGER,
      allowNull: true, // Allow null initially for existing records
    });

    await queryInterface.addColumn('comments', 'author_name', {
      type: Sequelize.STRING(255),
      allowNull: true, // Allow null initially for existing records
    });

    await queryInterface.addColumn('comments', 'date', {
      type: Sequelize.DATE,
      allowNull: true, // Allow null initially for existing records
    });

    await queryInterface.addColumn('comments', 'likes', {
      type: Sequelize.INTEGER,
      allowNull: false,
      defaultValue: 0,
    });

    // Add unique constraint on vk_comment_id after data migration
    // This will be done in a separate step to handle existing data
  },

  down: async (queryInterface, Sequelize) => {
    await queryInterface.removeColumn('comments', 'vk_comment_id');
    await queryInterface.removeColumn('comments', 'post_vk_id');
    await queryInterface.removeColumn('comments', 'owner_id');
    await queryInterface.removeColumn('comments', 'author_id');
    await queryInterface.removeColumn('comments', 'author_name');
    await queryInterface.removeColumn('comments', 'date');
    await queryInterface.removeColumn('comments', 'likes');
  }
};