'use client'

import { Navbar } from './Navbar'
import { useNotificationCount } from './useNotificationCount'

export function AppNavbar() {
  const notificationCount = useNotificationCount()

  return <Navbar notificationCount={notificationCount} />
}
