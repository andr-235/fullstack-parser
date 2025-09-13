import { ParserPage } from '@/features/parser'
import { useRouteAccess } from "@/shared/hooks/useRouteAccess";

export default function ParserRoute() {
  return <ParserPage />
}

// Force cache invalidation
export const dynamic = 'force-dynamic'
export const revalidate = 0
