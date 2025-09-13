import { useState, useEffect } from 'react'
import { httpClient } from '@/shared/lib/http-client'
import { User, CreateUserRequest, UpdateUserRequest, LoginRequest, AuthResponse } from './types'

export const useUser = () => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const login = async (credentials: LoginRequest): Promise<AuthResponse> => {
    setLoading(true)
    setError(null)
    try {
      const data = await httpClient.post<AuthResponse>('/api/auth/login', credentials)
      setUser(data.user)
      localStorage.setItem('token', data.token)
      return data
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('token')
  }

  const fetchCurrentUser = async () => {
    const token = localStorage.getItem('token')
    if (!token) return

    setLoading(true)
    try {
      const userData = await httpClient.get<User>('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      })
      setUser(userData)
    } catch (err) {
      logout()
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCurrentUser()
  }, [])

  return {
    user,
    loading,
    error,
    login,
    logout,
    refetch: fetchCurrentUser,
  }
}

export const useUsers = () => {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchUsers = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await httpClient.get<User[]>('/api/users')
      setUsers(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch users')
    } finally {
      setLoading(false)
    }
  }

  const createUser = async (userData: CreateUserRequest) => {
    try {
      const newUser = await httpClient.post<User>('/api/users', userData)
      setUsers(prev => [...prev, newUser])
      return newUser
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to create user')
    }
  }

  const updateUser = async (id: string, updates: UpdateUserRequest) => {
    try {
      const updatedUser = await httpClient.patch<User>(`/api/users/${id}`, updates)
      setUsers(prev => prev.map(user => (user.id === id ? updatedUser : user)))
      return updatedUser
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to update user')
    }
  }

  return {
    users,
    loading,
    error,
    fetchUsers,
    createUser,
    updateUser,
  }
}
