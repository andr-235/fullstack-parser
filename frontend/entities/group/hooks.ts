import { useState } from 'react'

import { Group, CreateGroupRequest, UpdateGroupRequest } from './types'

export const useGroups = () => {
  const [groups, setGroups] = useState<Group[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchGroups = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/groups')
      const data = await response.json()
      setGroups(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch groups')
    } finally {
      setLoading(false)
    }
  }

  const createGroup = async (groupData: CreateGroupRequest) => {
    try {
      const response = await fetch('/api/groups', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(groupData),
      })
      const newGroup = await response.json()
      setGroups(prev => [...prev, newGroup])
      return newGroup
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to create group')
    }
  }

  return {
    groups,
    loading,
    error,
    fetchGroups,
    createGroup,
  }
}
