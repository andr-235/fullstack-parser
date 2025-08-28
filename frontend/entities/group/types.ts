import { ID } from '@/shared/types'

export interface Group {
  id: ID
  name: string
  description: string
  ownerId: ID
  memberIds: ID[]
  isPrivate: boolean
  createdAt: string
  updatedAt: string
}

export interface CreateGroupRequest {
  name: string
  description: string
  isPrivate?: boolean
}

export interface UpdateGroupRequest {
  name?: string
  description?: string
  isPrivate?: boolean
}
