import { useCommentStore } from '../store';

// Селекторы для comment store
export const useComments = () => useCommentStore(state => state.comments);
export const useCurrentComment = () => useCommentStore(state => state.currentComment);
export const useCommentsLoading = () => useCommentStore(state => state.isLoading);
export const useCommentsError = () => useCommentStore(state => state.error);
export const useCommentsTotal = () => useCommentStore(state => state.total);

// Действия
export const useCommentActions = () => ({
  fetchComments: useCommentStore(state => state.fetchComments),
  fetchCommentById: useCommentStore(state => state.fetchCommentById),
  createComment: useCommentStore(state => state.createComment),
  updateComment: useCommentStore(state => state.updateComment),
  deleteComment: useCommentStore(state => state.deleteComment),
  fetchPostComments: useCommentStore(state => state.fetchPostComments),
  fetchCommentReplies: useCommentStore(state => state.fetchCommentReplies),
  clearError: useCommentStore(state => state.clearError),
  setCurrentComment: useCommentStore(state => state.setCurrentComment),
});