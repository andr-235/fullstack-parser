// Simple integration test without Jest
console.log('Testing module imports...');

try {
  // Test VK API module
  console.log('Loading VK API...');
  const vkApi = require('./src/repositories/vkApi.js');
  console.log('✓ VK API loaded successfully');

  // Test DB Repo
  console.log('Loading DB Repo...');
  const dbRepo = require('./src/repositories/dbRepo.js');
  console.log('✓ DB Repo loaded successfully');

  // Test VK Service
  console.log('Loading VK Service...');
  const vkService = require('./src/services/vkService.js');
  console.log('✓ VK Service loaded successfully');

  // Test Task Service
  console.log('Loading Task Service...');
  const taskService = require('./src/services/taskService.js');
  console.log('✓ Task Service loaded successfully');

  // Test Queue
  console.log('Loading Queue...');
  const { queue, worker } = require('./config/queue.js');
  console.log('✓ Queue loaded successfully');

  // Test Models
  console.log('Loading Models...');
  const { sequelize, Post, Comment, Task } = require('./src/models/index.js');
  console.log('✓ Models loaded successfully');

  // Test Task Controller
  console.log('Loading Task Controller...');
  const taskController = require('./src/controllers/taskController.js');
  console.log('✓ Task Controller loaded successfully');

  // Check methods exist
  console.log('\nChecking critical methods...');
  if (typeof vkService.collectForTask !== 'function') {
    throw new Error('vkService.collectForTask is not a function');
  }
  console.log('✓ vkService.collectForTask exists');

  if (typeof dbRepo.upsertPosts !== 'function') {
    throw new Error('dbRepo.upsertPosts is not a function');
  }
  console.log('✓ dbRepo.upsertPosts exists');

  if (typeof dbRepo.upsertComments !== 'function') {
    throw new Error('dbRepo.upsertComments is not a function');
  }
  console.log('✓ dbRepo.upsertComments exists');

  if (typeof taskService.createTask !== 'function') {
    throw new Error('taskService.createTask is not a function');
  }
  console.log('✓ taskService.createTask exists');

  // Check model structure
  console.log('\nChecking model attributes...');
  if (!Post.rawAttributes.vk_post_id) {
    throw new Error('Post model missing vk_post_id field');
  }
  console.log('✓ Post.vk_post_id field exists');

  if (!Comment.rawAttributes.vk_comment_id) {
    throw new Error('Comment model missing vk_comment_id field');
  }
  console.log('✓ Comment.vk_comment_id field exists');

  if (!Task.rawAttributes.finishedAt) {
    throw new Error('Task model missing finishedAt field');
  }
  console.log('✓ Task.finishedAt field exists');

  console.log('\n🎉 All integration tests passed!');

} catch (error) {
  console.error('\n❌ Integration test failed:', error.message);
  console.error(error.stack);
  process.exit(1);
}