'use client'

import { useState } from 'react'
import { GroupsList } from '@/features/groups/ui/GroupsList'
import { GroupsFilters } from '@/features/groups/ui/GroupsFilters'
import { useGroups } from '@/entities/groups'
import { GroupsFilters as GroupsFiltersType } from '@/entities/groups'
import { Button } from '@/shared/ui'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/shared/ui'
import { GroupForm } from '@/features/groups/ui/GroupForm'
import { FileUploadModal } from '@/shared/ui'
import { Plus, Upload, RefreshCw } from 'lucide-react'
import { Alert, AlertDescription } from '@/shared/ui'

export function GroupsPage() {
 const [filters, setFilters] = useState<GroupsFiltersType>({
  active_only: true,
 })
 const [showCreateForm, setShowCreateForm] = useState(false)

 const {
  groups,
  loading,
  error,
  createGroup,
  updateGroup,
  deleteGroup,
  toggleGroupStatus,
  refetch,
 } = useGroups(filters)

 const handleCreateGroup = async (data: any) => {
  try {
   await createGroup(data)
   setShowCreateForm(false)
   refetch()
  } catch (err) {
   console.error('Failed to create group:', err)
   throw err
  }
 }

 const handleUpdateGroup = async (id: number, updates: any) => {
  try {
   await updateGroup(id, updates)
   refetch()
  } catch (err) {
   console.error('Failed to update group:', err)
   throw err
  }
 }

 const handleDeleteGroup = async (id: number) => {
  try {
   await deleteGroup(id)
   refetch()
  } catch (err) {
   console.error('Failed to delete group:', err)
   throw err
  }
 }

 const handleToggleStatus = async (id: number, isActive: boolean) => {
  try {
   await toggleGroupStatus(id, isActive)
   refetch()
  } catch (err) {
   console.error('Failed to toggle group status:', err)
   throw err
  }
 }

 const handleFiltersChange = (newFilters: GroupsFiltersType) => {
  setFilters(newFilters)
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
       max_posts_to_check: 100,
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
    onUpdate={handleUpdateGroup}
    onDelete={handleDeleteGroup}
    onToggleStatus={handleToggleStatus}
   />
  </div>
 )
}
