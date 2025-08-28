'use client'

import { createContext, useContext, ReactNode } from 'react'
import { useUser } from '@/entities/user'

interface AuthContextType {
 user: ReturnType<typeof useUser>['user']
 loading: boolean
 login: ReturnType<typeof useUser>['login']
 logout: ReturnType<typeof useUser>['logout']
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
 children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
 const { user, loading, login, logout } = useUser()

 return (
  <AuthContext.Provider value={{ user, loading, login, logout }}>
   {children}
  </AuthContext.Provider>
 )
}

export function useAuth() {
 const context = useContext(AuthContext)
 if (context === undefined) {
  throw new Error('useAuth must be used within an AuthProvider')
 }
 return context
}
