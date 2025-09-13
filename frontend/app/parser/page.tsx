import { ParserPage } from '@/features/parser'

export default function ParserRoute() {
  return <ParserPage />
}

export const dynamic = 'force-dynamic'
export const revalidate = 0
