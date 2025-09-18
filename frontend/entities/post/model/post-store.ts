import { usePostStore } from '../store';

// Селекторы для post store
export const usePosts = () => usePostStore(state => state.posts);
export const useCurrentPost = () => usePostStore(state => state.currentPost);
export const usePostsLoading = () => usePostStore(state => state.isLoading);
export const usePostsError = () => usePostStore(state => state.error);
export const usePostsTotal = () => usePostStore(state => state.total);

// Действия
export const usePostActions = () => ({
  fetchPosts: usePostStore(state => state.fetchPosts),
  fetchPostById: usePostStore(state => state.fetchPostById),
  createPost: usePostStore(state => state.createPost),
  updatePost: usePostStore(state => state.updatePost),
  deletePost: usePostStore(state => state.deletePost),
  fetchGroupPosts: usePostStore(state => state.fetchGroupPosts),
  fetchUserPosts: usePostStore(state => state.fetchUserPosts),
  clearError: usePostStore(state => state.clearError),
  setCurrentPost: usePostStore(state => state.setCurrentPost),
});