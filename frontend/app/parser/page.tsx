import { ParserPage } from '@/widgets/parser-page'

export default function ParserRoute() {
  return <ParserPage />
}

// Force cache invalidation
export const dynamic = 'force-dynamic'
export const revalidate = 0
