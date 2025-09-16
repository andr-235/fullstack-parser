import { useAuthorStore } from '../store';

// Селекторы для author store
export const useAuthors = () => useAuthorStore(state => state.authors);
export const useCurrentAuthor = () => useAuthorStore(state => state.currentAuthor);
export const useAuthorsLoading = () => useAuthorStore(state => state.isLoading);
export const useAuthorsError = () => useAuthorStore(state => state.error);
export const useAuthorsTotal = () => useAuthorStore(state => state.total);

// Действия
export const useAuthorActions = () => ({
  fetchAuthors: useAuthorStore(state => state.fetchAuthors),
  fetchAuthorById: useAuthorStore(state => state.fetchAuthorById),
  createAuthor: useAuthorStore(state => state.createAuthor),
  updateAuthor: useAuthorStore(state => state.updateAuthor),
  deleteAuthor: useAuthorStore(state => state.deleteAuthor),
  fetchAuthorByVkId: useAuthorStore(state => state.fetchAuthorByVkId),
  searchAuthors: useAuthorStore(state => state.searchAuthors),
  clearError: useAuthorStore(state => state.clearError),
  setCurrentAuthor: useAuthorStore(state => state.setCurrentAuthor),
});