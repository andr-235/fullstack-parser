import { DashboardPage } from '@/features/dashboard'

export default function DashboardRoute() {
  return <DashboardPage />
}

// Force cache invalidation
export const dynamic = 'force-dynamic'
export const revalidate = 0
