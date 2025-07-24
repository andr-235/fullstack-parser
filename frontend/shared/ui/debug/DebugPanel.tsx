'use client'

import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'

interface DebugPanelProps {
 isVisible?: boolean
}

export function DebugPanel({ isVisible = false }: DebugPanelProps) {
 const [isOpen, setIsOpen] = useState(isVisible)
 const queryClient = useQueryClient()

 if (process.env.NODE_ENV !== 'development') {
  return null
 }

 const clearCache = () => {
  queryClient.clear()
  console.log('Кеш React Query очищен')
 }

 const getCacheInfo = () => {
  const queries = queryClient.getQueryCache().getAll()
  const mutations = queryClient.getMutationCache().getAll()

  return {
   queries: queries.length,
   mutations: mutations.length,
   cacheSize: JSON.stringify(queryClient.getQueryCache().getAll()).length,
  }
 }

 const cacheInfo = getCacheInfo()

 return (
  <>
   {/* Кнопка открытия панели */}
   <button
    onClick={() => setIsOpen(!isOpen)}
    className="fixed bottom-4 right-4 z-50 bg-blue-600 text-white p-2 rounded-full shadow-lg hover:bg-blue-700"
    title="Отладка"
   >
    <svg
     className="w-6 h-6"
     fill="none"
     stroke="currentColor"
     viewBox="0 0 24 24"
    >
     <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
     />
     <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
     />
    </svg>
   </button>

   {/* Панель отладки */}
   {isOpen && (
    <div className="fixed bottom-20 right-4 z-50 bg-white border border-gray-300 rounded-lg shadow-xl p-4 w-80 max-h-96 overflow-y-auto">
     <div className="flex justify-between items-center mb-4">
      <h3 className="text-lg font-semibold text-gray-900">Отладка</h3>
      <button
       onClick={() => setIsOpen(false)}
       className="text-gray-500 hover:text-gray-700"
      >
       ✕
      </button>
     </div>

     <div className="space-y-4">
      {/* Информация о кеше */}
      <div className="bg-gray-50 p-3 rounded">
       <h4 className="font-medium text-gray-900 mb-2">React Query Кеш</h4>
       <div className="text-sm text-gray-600 space-y-1">
        <div>Запросы: {cacheInfo.queries}</div>
        <div>Мутации: {cacheInfo.mutations}</div>
        <div>Размер: {Math.round(cacheInfo.cacheSize / 1024)}KB</div>
       </div>
       <button
        onClick={clearCache}
        className="mt-2 text-xs bg-red-600 text-white px-2 py-1 rounded hover:bg-red-700"
       >
        Очистить кеш
       </button>
      </div>

      {/* Информация об окружении */}
      <div className="bg-gray-50 p-3 rounded">
       <h4 className="font-medium text-gray-900 mb-2">Окружение</h4>
       <div className="text-sm text-gray-600 space-y-1">
        <div>API URL: {process.env.NEXT_PUBLIC_API_URL}</div>
        <div>NODE_ENV: {process.env.NODE_ENV}</div>
        <div>Время: {new Date().toLocaleTimeString()}</div>
       </div>
      </div>

      {/* Действия */}
      <div className="bg-gray-50 p-3 rounded">
       <h4 className="font-medium text-gray-900 mb-2">Действия</h4>
       <div className="space-y-2">
        <button
         onClick={() => window.location.reload()}
         className="w-full text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700"
        >
         Обновить страницу
        </button>
        <button
         onClick={() => {
          localStorage.clear()
          sessionStorage.clear()
          window.location.reload()
         }}
         className="w-full text-xs bg-orange-600 text-white px-2 py-1 rounded hover:bg-orange-700"
        >
         Очистить хранилище
        </button>
        <button
         onClick={() => {
          console.clear()
          console.log('Консоль очищена')
         }}
         className="w-full text-xs bg-gray-600 text-white px-2 py-1 rounded hover:bg-gray-700"
        >
         Очистить консоль
        </button>
       </div>
      </div>
     </div>
    </div>
   )}
  </>
 )
} 