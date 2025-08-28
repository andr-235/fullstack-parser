import { KeywordsPage } from '@/features/keywords'

export default function KeywordsRoute() {
  return <KeywordsPage />
}

// Force cache invalidation
export const dynamic = 'force-dynamic'
export const revalidate = 0
