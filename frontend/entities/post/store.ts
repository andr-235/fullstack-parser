/**
 * Модуль Zustand store для управления состоянием постов.
 *
 * Зависимости:
 * - postApi: API клиент для взаимодействия с сервером постов (из './api')
 * - Типы: Post, PostCreateRequest, PostUpdateRequest, PostListResponse, PostFilters (из './types')
 */

import { create } from 'zustand';
import { postApi } from './api';
import type {
  Post,
  PostCreateRequest,
  PostUpdateRequest,
  PostListResponse,
  PostFilters
} from './types';

/**
 * Интерфейс состояния постов для Zustand store.
 *
 * Определяет структуру состояния и доступные действия для управления постами,
 * включая загрузку, создание, обновление и удаление постов.
 */
interface PostState {
  /** Массив загруженных постов */
  posts: Post[];
  /** Текущий выбранный пост */
  currentPost: Post | null;
  /** Флаг загрузки операций */
  isLoading: boolean;
  /** Сообщение об ошибке, если операция завершилась неудачно */
  error: string | null;
  /** Общее количество постов (для пагинации) */
  total: number;

  // Actions
  /** Загружает список постов с опциональными фильтрами */
  fetchPosts: (filters?: PostFilters) => Promise<void>;
  /** Загружает пост по ID */
  fetchPostById: (id: string) => Promise<void>;
  /** Создает новый пост */
  createPost: (data: PostCreateRequest) => Promise<Post>;
  /** Обновляет существующий пост */
  updatePost: (id: string, data: PostUpdateRequest) => Promise<Post>;
  /** Удаляет пост по ID */
  deletePost: (id: string) => Promise<void>;
  /** Загружает посты группы */
  fetchGroupPosts: (groupId: string, limit?: number, offset?: number) => Promise<void>;
  /** Загружает посты пользователя */
  fetchUserPosts: (userId: string, limit?: number, offset?: number) => Promise<void>;
  /** Очищает сообщение об ошибке */
  clearError: () => void;
  /** Устанавливает текущий пост */
  setCurrentPost: (post: Post | null) => void;
}

/**
 * Zustand store для управления состоянием постов.
 *
 * Предоставляет методы для загрузки, создания, обновления и удаления постов,
 * а также управления состоянием загрузки и ошибок.
 */
export const usePostStore = create<PostState>((set, get) => ({
  posts: [],
  currentPost: null,
  isLoading: false,
  error: null,
  total: 0,

  /**
   * Загружает список постов с опциональными фильтрами.
   *
   * @param {PostFilters} [filters={}] - Фильтры для запроса постов (например, по автору, дате и т.д.)
   * @returns {Promise<void>} Промис, который разрешается после загрузки постов
   * @throws {Error} Ошибка API или сети при загрузке постов
   * @example
   * ```typescript
   * const store = usePostStore();
   * await store.fetchPosts({ authorId: '123', limit: 10 });
   * ```
   */
  fetchPosts: async (filters = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response: PostListResponse = await postApi.getPosts(filters);
      set({
        posts: response.posts,
        total: response.total,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка загрузки постов';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  /**
   * Загружает пост по его уникальному идентификатору.
   *
   * @param {string} id - Уникальный идентификатор поста
   * @returns {Promise<void>} Промис, который разрешается после загрузки поста
   * @throws {Error} Ошибка API или сети при загрузке поста
   * @example
   * ```typescript
   * const store = usePostStore();
   * await store.fetchPostById('post-123');
   * ```
   */
  fetchPostById: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const post: Post = await postApi.getPostById(id);
      set({
        currentPost: post,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка загрузки поста';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  /**
   * Создает новый пост и добавляет его в начало списка постов.
   *
   * @param {PostCreateRequest} data - Данные для создания поста (текст, заголовок и т.д.)
   * @returns {Promise<Post>} Промис, который разрешается созданным постом
   * @throws {Error} Ошибка API или сети при создании поста
   * @example
   * ```typescript
   * const store = usePostStore();
   * const newPost = await store.createPost({
   *   title: 'Новый пост',
   *   content: 'Содержимое поста'
   * });
   * ```
   */
  createPost: async (data: PostCreateRequest) => {
    set({ isLoading: true, error: null });
    try {
      const post: Post = await postApi.createPost(data);
      const { posts } = get();
      // Добавляем новый пост в начало списка для отображения в интерфейсе
      set({
        posts: [post, ...posts],
        isLoading: false
      });
      return post;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка создания поста';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  /**
   * Обновляет существующий пост и синхронизирует изменения в состоянии.
   *
   * @param {string} id - Уникальный идентификатор поста для обновления
   * @param {PostUpdateRequest} data - Данные для обновления поста
   * @returns {Promise<Post>} Промис, который разрешается обновленным постом
   * @throws {Error} Ошибка API или сети при обновлении поста
   * @example
   * ```typescript
   * const store = usePostStore();
   * const updatedPost = await store.updatePost('post-123', {
   *   title: 'Обновленный заголовок'
   * });
   * ```
   */
  updatePost: async (id: string, data: PostUpdateRequest) => {
    set({ isLoading: true, error: null });
    try {
      const post: Post = await postApi.updatePost(id, data);
      const { posts } = get();
      // Обновляем пост в массиве, заменяя старый объект на новый
      const updatedPosts = posts.map(p => p.id === id ? post : p);
      set({
        posts: updatedPosts,
        currentPost: post,
        isLoading: false
      });
      return post;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка обновления поста';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  /**
   * Удаляет пост и обновляет состояние, удаляя его из списка.
   *
   * @param {string} id - Уникальный идентификатор поста для удаления
   * @returns {Promise<void>} Промис, который разрешается после удаления поста
   * @throws {Error} Ошибка API или сети при удалении поста
   * @example
   * ```typescript
   * const store = usePostStore();
   * await store.deletePost('post-123');
   * ```
   */
  deletePost: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await postApi.deletePost(id);
      const { posts } = get();
      // Фильтруем массив, удаляя пост с указанным ID
      const filteredPosts = posts.filter(p => p.id !== id);
      set({
        posts: filteredPosts,
        currentPost: null,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка удаления поста';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  /**
   * Загружает посты конкретной группы с поддержкой пагинации.
   *
   * @param {string} groupId - Уникальный идентификатор группы
   * @param {number} [limit=50] - Максимальное количество постов для загрузки
   * @param {number} [offset=0] - Смещение для пагинации (количество пропускаемых постов)
   * @returns {Promise<void>} Промис, который разрешается после загрузки постов группы
   * @throws {Error} Ошибка API или сети при загрузке постов группы
   * @example
   * ```typescript
   * const store = usePostStore();
   * await store.fetchGroupPosts('group-123', 20, 0);
   * ```
   */
  fetchGroupPosts: async (groupId: string, limit = 50, offset = 0) => {
    set({ isLoading: true, error: null });
    try {
      const response: PostListResponse = await postApi.getGroupPosts(groupId, limit, offset);
      set({
        posts: response.posts,
        total: response.total,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка загрузки постов группы';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  /**
   * Загружает посты конкретного пользователя с поддержкой пагинации.
   *
   * @param {string} userId - Уникальный идентификатор пользователя
   * @param {number} [limit=50] - Максимальное количество постов для загрузки
   * @param {number} [offset=0] - Смещение для пагинации (количество пропускаемых постов)
   * @returns {Promise<void>} Промис, который разрешается после загрузки постов пользователя
   * @throws {Error} Ошибка API или сети при загрузке постов пользователя
   * @example
   * ```typescript
   * const store = usePostStore();
   * await store.fetchUserPosts('user-456', 10, 20);
   * ```
   */
  fetchUserPosts: async (userId: string, limit = 50, offset = 0) => {
    set({ isLoading: true, error: null });
    try {
      const response: PostListResponse = await postApi.getUserPosts(userId, limit, offset);
      set({
        posts: response.posts,
        total: response.total,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка загрузки постов пользователя';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  /**
   * Очищает текущее сообщение об ошибке в состоянии.
   *
   * Используется для сброса ошибок после их обработки или при повторных попытках операций.
   *
   * @returns {void}
   * @example
   * ```typescript
   * const store = usePostStore();
   * store.clearError();
   * ```
   */
  clearError: () => {
    set({ error: null });
  },

  /**
   * Устанавливает текущий выбранный пост.
   *
   * Используется для выделения поста в интерфейсе или для детального просмотра.
   *
   * @param {Post | null} post - Пост для установки как текущий, или null для сброса
   * @returns {void}
   * @example
   * ```typescript
   * const store = usePostStore();
   * store.setCurrentPost(selectedPost);
   * ```
   */
  setCurrentPost: (post: Post | null) => {
    set({ currentPost: post });
  },
}));