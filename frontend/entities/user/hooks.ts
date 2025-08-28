import { useState, useEffect } from 'react'
import {
  User,
  CreateUserRequest,
  UpdateUserRequest,
  LoginRequest,
  AuthResponse,
} from './types'

export const useUser = () => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const login = async (credentials: LoginRequest): Promise<AuthResponse> => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      })

      if (!response.ok) {
        throw new Error('Invalid credentials')
      }

      const data: AuthResponse = await response.json()
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
      const response = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (response.ok) {
        const userData: User = await response.json()
        setUser(userData)
      } else {
        logout() // Invalid token
      }
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
      const response = await fetch('/api/users')
      const data = await response.json()
      setUsers(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch users')
    } finally {
      setLoading(false)
    }
  }

  const createUser = async (userData: CreateUserRequest) => {
    try {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      })
      const newUser = await response.json()
      setUsers((prev) => [...prev, newUser])
      return newUser
    } catch (err) {
      throw new Error(
        err instanceof Error ? err.message : 'Failed to create user'
      )
    }
  }

  const updateUser = async (id: string, updates: UpdateUserRequest) => {
    try {
      const response = await fetch(`/api/users/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      })
      const updatedUser = await response.json()
      setUsers((prev) =>
        prev.map((user) => (user.id === id ? updatedUser : user))
      )
      return updatedUser
    } catch (err) {
      throw new Error(
        err instanceof Error ? err.message : 'Failed to update user'
      )
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
