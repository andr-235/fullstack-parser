import { CommentsPage } from '@/features/comments'

export default function CommentsRoute() {
  return <CommentsPage />
}

// Force cache invalidation
export const dynamic = 'force-dynamic'
export const revalidate = 0
