module.exports = {
  up: async (queryInterface, Sequelize) => {
    // Add new VK-specific fields to posts table
    await queryInterface.addColumn('posts', 'vk_post_id', {
      type: Sequelize.INTEGER,
      allowNull: true, // Allow null initially for existing records
    });

    await queryInterface.addColumn('posts', 'owner_id', {
      type: Sequelize.INTEGER,
      allowNull: true, // Allow null initially for existing records
    });

    await queryInterface.addColumn('posts', 'group_id', {
      type: Sequelize.INTEGER,
      allowNull: true, // Allow null initially for existing records
    });

    await queryInterface.addColumn('posts', 'date', {
      type: Sequelize.DATE,
      allowNull: true, // Allow null initially for existing records
    });

    await queryInterface.addColumn('posts', 'likes', {
      type: Sequelize.INTEGER,
      allowNull: false,
      defaultValue: 0,
    });

    // Add unique constraint on vk_post_id after data migration
    // This will be done in a separate step to handle existing data
  },

  down: async (queryInterface, Sequelize) => {
    await queryInterface.removeColumn('posts', 'vk_post_id');
    await queryInterface.removeColumn('posts', 'owner_id');
    await queryInterface.removeColumn('posts', 'group_id');
    await queryInterface.removeColumn('posts', 'date');
    await queryInterface.removeColumn('posts', 'likes');
  }
};