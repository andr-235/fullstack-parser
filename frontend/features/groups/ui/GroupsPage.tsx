'use client'

import { useState } from 'react'

import { Plus, RefreshCw } from 'lucide-react'

import { Button } from '@/shared/ui'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/shared/ui'
import { FileUploadModal } from '@/shared/ui'
import { Alert, AlertDescription } from '@/shared/ui'
import { Pagination } from '@/shared/ui'

import { GroupsFilters as GroupsFiltersType, UpdateGroupRequest } from '@/entities/groups'
import { useGroups } from '@/entities/groups'

import { GroupForm } from '@/features/groups/ui/GroupForm'
import { GroupsFilters } from '@/features/groups/ui/GroupsFilters'
import { GroupsList } from '@/features/groups/ui/GroupsList'

export function GroupsPage() {
 const [filters, setFilters] = useState<GroupsFiltersType>({
  active_only: true,
  page: 1,
  size: 20,
 })
 const [showCreateForm, setShowCreateForm] = useState(false)

 const {
  groups,
  loading,
  error,
  pagination,
  createGroup,
  updateGroup,
  deleteGroup,
  toggleGroupStatus,
  refetch,
 } = useGroups(filters)

 const handleCreateGroup = async (data: {
  vk_id_or_screen_name: string
  name?: string | undefined
  screen_name?: string | undefined
  description?: string | undefined
  is_active?: boolean | undefined
  max_posts_to_check?: number | undefined
 }) => {
  try {
   // Преобразуем данные формы в CreateGroupRequest
   const vkId = parseInt(data.vk_id_or_screen_name)
   if (isNaN(vkId)) {
    throw new Error('VK ID должен быть числом')
   }

   const createData = {
    vk_id: vkId,
    name: data.name || '',
    screen_name: data.screen_name || '',
    ...(data.description && { description: data.description }),
   }

   await createGroup(createData)
   setShowCreateForm(false)
   refetch()
  } catch (err) {
   // eslint-disable-next-line no-console
   console.error('Failed to create group:', err)
   throw err
  }
 }

 const handleUpdateGroup = async (id: number, updates: UpdateGroupRequest) => {
  try {
   await updateGroup(id, updates)
   refetch()
  } catch (err) {
   // eslint-disable-next-line no-console
   console.error('Failed to update group:', err)
   throw err
  }
 }

 const handleDeleteGroup = async (id: number) => {
  try {
   await deleteGroup(id)
   refetch()
  } catch (err) {
   // eslint-disable-next-line no-console
   console.error('Failed to delete group:', err)
   throw err
  }
 }

 const handleToggleStatus = async (id: number, isActive: boolean) => {
  try {
   await toggleGroupStatus(id, isActive)
   refetch()
  } catch (err) {
   // eslint-disable-next-line no-console
   console.error('Failed to toggle group status:', err)
   throw err
  }
 }

 const handleFiltersChange = (newFilters: GroupsFiltersType) => {
  setFilters({ ...newFilters, page: 1 }) // Сбрасываем на первую страницу при изменении фильтров
 }

 const handlePageChange = (page: number) => {
  setFilters(prev => ({ ...prev, page }))
 }

 const handleRefresh = () => {
  refetch()
 }

 return (
  <div className="container mx-auto py-6 space-y-6">
   {/* Header */}
   <div className="flex items-center justify-between">
    <div>
     <h1 className="text-3xl font-bold tracking-tight">Группы VK</h1>
     <p className="text-muted-foreground">
      Управление группами VK для мониторинга комментариев
     </p>
    </div>

    <div className="flex items-center gap-2">
     <Button variant="outline" onClick={handleRefresh}>
      <RefreshCw className="mr-2 h-4 w-4" />
      Обновить
     </Button>

     <FileUploadModal
      type="groups"
      triggerText="Загрузить из файла"
      onSuccess={handleRefresh}
      apiParams={{
       is_active: true,
       max_posts_to_check: 10,
      }}
     />

     <Dialog open={showCreateForm} onOpenChange={setShowCreateForm}>
      <DialogTrigger asChild>
       <Button>
        <Plus className="mr-2 h-4 w-4" />
        Добавить группу
       </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md">
       <DialogHeader>
        <DialogTitle>Добавить новую группу VK</DialogTitle>
       </DialogHeader>
       <GroupForm
        onSubmit={handleCreateGroup}
        onCancel={() => setShowCreateForm(false)}
       />
      </DialogContent>
     </Dialog>
    </div>
   </div>

   {/* Filters */}
   <Card>
    <CardHeader>
     <CardTitle className="text-lg">Фильтры</CardTitle>
    </CardHeader>
    <CardContent>
     <GroupsFilters
      filters={filters}
      onFiltersChange={handleFiltersChange}
     />
    </CardContent>
   </Card>

   {/* Error State */}
   {error && (
    <Alert className="border-destructive">
     <AlertDescription>
      Ошибка загрузки групп: {error}
      <Button
       variant="outline"
       size="sm"
       onClick={handleRefresh}
       className="ml-4"
      >
       Попробовать снова
      </Button>
     </AlertDescription>
    </Alert>
   )}

   {/* Groups List */}
   <GroupsList
    groups={groups}
    loading={loading}
    totalGroups={pagination.total}
    totalActiveGroups={groups.filter(g => g.is_active).length}
    onUpdate={handleUpdateGroup}
    onDelete={handleDeleteGroup}
    onToggleStatus={handleToggleStatus}
   />

   {/* Pagination */}
   {pagination.pages > 1 && (
    <div className="mt-6">
     <Pagination
      currentPage={pagination.page}
      totalPages={pagination.pages}
      totalItems={pagination.total}
      itemsPerPage={pagination.size}
      onPageChange={handlePageChange}
     />
    </div>
   )}
  </div>
 )
}
