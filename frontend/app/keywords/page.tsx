import KeywordsPage from '@/features/keywords/ui/KeywordsPage'

export default function KeywordsRoute() {
  return <KeywordsPage />
}

// Force cache invalidation
export const dynamic = 'force-dynamic'
export const revalidate = 0
