import ParserPage from '@/features/parser/ui/ParserPage'

export default function ParserRoute() {
  return <ParserPage />
}

// Force cache invalidation
export const dynamic = 'force-dynamic'
export const revalidate = 0
