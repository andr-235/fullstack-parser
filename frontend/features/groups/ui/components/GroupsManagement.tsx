import React, { useState } from 'react'
import {
 Card,
 CardContent,
 CardHeader,
 CardTitle,
} from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { LoadingSpinner } from '@/shared/ui'
import { Search, Plus } from 'lucide-react'
import { UploadGroupsModal } from './UploadGroupsModal'
import { useCreateGroup } from '../../hooks'
import { toast } from 'react-hot-toast'
import type { GroupsManagementProps } from '../../types'

export function GroupsManagement({
 searchTerm,
 onSearchChange,
 activeOnly,
 onActiveOnlyChange,
}: GroupsManagementProps) {
 const [newGroupUrl, setNewGroupUrl] = useState('')
 const createGroupMutation = useCreateGroup()

 const handleAddGroup = (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault()
  if (!newGroupUrl.trim()) return

  createGroupMutation.mutate(
   {
    vk_id_or_screen_name: newGroupUrl,
    is_active: true,
    max_posts_to_check: 100,
   },
   {
    onSuccess: () => {
     setNewGroupUrl('')
     toast.success('Группа успешно добавлена! 🎉')
    },
    onError: (error: any) => {
     console.error('Ошибка создания группы:', error)
     let errorMessage = 'Ошибка при создании группы'

     if (error?.status === 409 || error?.response?.status === 409) {
      errorMessage = error?.response?.data?.detail || 'Группа уже существует в системе'
     } else if (error?.response?.data?.detail) {
      errorMessage = error.response.data.detail
     } else if (error?.message) {
      errorMessage = error.message
     }

     toast.error(errorMessage)
    },
   }
  )
 }

 return (
  <Card className="border-slate-700 bg-slate-800 shadow-lg">
   <CardHeader className="pb-4">
    <CardTitle className="text-lg font-semibold text-slate-200">
     Управление группами
    </CardTitle>
   </CardHeader>
   <CardContent className="space-y-4">
    {/* Поиск и фильтры */}
    <div className="flex flex-col lg:flex-row gap-4">
     <div className="flex-1 relative">
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
      <Input
       placeholder="Поиск по названию или screen_name..."
       className="pl-10 border-slate-600 bg-slate-700 text-slate-200 focus:border-blue-500 focus:ring-blue-500 placeholder-slate-400"
       value={searchTerm}
       onChange={(e) => onSearchChange(e.target.value)}
      />
     </div>

     <div className="flex items-center space-x-4">
      <label className="flex items-center space-x-2 text-sm text-slate-300">
       <input
        type="checkbox"
        checked={activeOnly}
        onChange={() => onActiveOnlyChange(!activeOnly)}
        className="rounded border-slate-600 bg-slate-700 text-blue-500 focus:ring-blue-500"
       />
       <span>Только активные</span>
      </label>

      <UploadGroupsModal onSuccess={() => { }} />
     </div>
    </div>

    {/* Добавление новой группы */}
    <form onSubmit={handleAddGroup} className="flex gap-2">
     <Input
      placeholder="https://vk.com/example или example"
      value={newGroupUrl}
      onChange={(e) => setNewGroupUrl(e.target.value)}
      disabled={createGroupMutation.isPending}
      className="flex-1 border-slate-600 bg-slate-700 text-slate-200 focus:border-blue-500 focus:ring-blue-500 placeholder-slate-400"
     />
     <Button
      type="submit"
      disabled={createGroupMutation.isPending}
      className="bg-blue-600 hover:bg-blue-700 text-white px-6 transition-all duration-200 hover:scale-105"
     >
      {createGroupMutation.isPending ? (
       <LoadingSpinner className="h-4 w-4" />
      ) : (
       <Plus className="h-4 w-4" />
      )}
      <span className="ml-2">Добавить</span>
     </Button>
    </form>
   </CardContent>
  </Card>
 )
} 