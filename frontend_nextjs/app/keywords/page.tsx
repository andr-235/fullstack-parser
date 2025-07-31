import { KeywordsPage } from '@/widgets/keywords-page'

export default function KeywordsRoute() {
  return <KeywordsPage />
}

// Force cache invalidation
export const dynamic = 'force-dynamic'
export const revalidate = 0
