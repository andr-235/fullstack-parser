import { GroupsPage } from '@/widgets/groups-page'

export default function GroupsRoute() {
  return <GroupsPage />
}

// Force cache invalidation
export const dynamic = 'force-dynamic'
export const revalidate = 0
