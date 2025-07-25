// Экспорт типов
export type {
  VKCommentResponse,
  VKCommentBase,
  CommentWithKeywords,
  CommentSearchParams,
} from './types'

// Экспорт модели
export { Comment } from './model'

// Экспорт хуков
export {
  useComments,
  useInfiniteComments,
  useUpdateCommentStatus,
  useMarkCommentAsViewed,
  useArchiveComment,
  useUnarchiveComment,
  useCommentWithKeywords,
} from './hooks'

// Экспорт bulk операций
export {
  useBulkMarkAsViewed,
  useBulkArchive,
  useBulkUnarchive,
  useBulkDelete,
} from './hooks/bulk-operations'
