'use client'

import { Keyword } from '@/entities/keywords'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Skeleton } from '@/shared/ui'
import { Alert, AlertDescription } from '@/shared/ui'
import { KeywordCard } from '@/features/keywords/ui/KeywordCard'
import { Hash, MessageSquare, FolderOpen } from 'lucide-react'

interface KeywordsListProps {
 keywords: Keyword[]
 loading?: boolean
 onUpdate?: (id: number, updates: any) => void
 onDelete?: (id: number) => void
 onToggleStatus?: (id: number, isActive: boolean) => void
}

export function KeywordsList({
 keywords,
 loading,
 onUpdate,
 onDelete,
 onToggleStatus
}: KeywordsListProps) {
 if (loading) {
  return (
   <div className="space-y-4">
    {[...Array(3)].map((_, i) => (
     <Card key={i}>
      <CardHeader>
       <div className="flex items-center justify-between">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-8 w-8" />
       </div>
      </CardHeader>
      <CardContent>
       <Skeleton className="h-4 w-full mb-2" />
       <Skeleton className="h-4 w-3/4" />
      </CardContent>
     </Card>
    ))}
   </div>
  )
 }

 if (keywords.length === 0) {
  return (
   <Card>
    <CardContent className="py-12">
     <div className="text-center space-y-4">
      <Hash className="mx-auto h-16 w-16 text-muted-foreground" />
      <div>
       <h3 className="text-lg font-medium">Ключевые слова не найдены</h3>
       <p className="text-muted-foreground">
        {loading ? 'Загрузка ключевых слов...' : 'Добавьте свое первое ключевое слово для начала мониторинга комментариев'}
       </p>
      </div>
     </div>
    </CardContent>
   </Card>
  )
 }

 return (
  <div className="space-y-4">
   {/* Summary Stats */}
   <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
    <Card>
     <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">Всего ключевых слов</CardTitle>
      <Hash className="h-4 w-4 text-muted-foreground" />
     </CardHeader>
     <CardContent>
      <div className="text-2xl font-bold">{keywords.length}</div>
     </CardContent>
    </Card>

    <Card>
     <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">Активные ключевые слова</CardTitle>
      <FolderOpen className="h-4 w-4 text-muted-foreground" />
     </CardHeader>
     <CardContent>
      <div className="text-2xl font-bold">
       {keywords.filter(k => k.is_active).length}
      </div>
     </CardContent>
    </Card>

    <Card>
     <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">Всего совпадений</CardTitle>
      <MessageSquare className="h-4 w-4 text-muted-foreground" />
     </CardHeader>
     <CardContent>
      <div className="text-2xl font-bold">
       {keywords.reduce((sum, keyword) => sum + keyword.total_matches, 0).toLocaleString()}
      </div>
     </CardContent>
    </Card>

    <Card>
     <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">Категории</CardTitle>
      <FolderOpen className="h-4 w-4 text-muted-foreground" />
     </CardHeader>
     <CardContent>
      <div className="text-2xl font-bold">
       {new Set(keywords.map(k => k.category).filter(Boolean)).size}
      </div>
     </CardContent>
    </Card>
   </div>

   {/* Keywords Grid */}
   <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
    {keywords.map((keyword) => (
     <KeywordCard
      key={keyword.id}
      keyword={keyword}
      onUpdate={onUpdate || (() => { })}
      onDelete={onDelete || (() => { })}
      onToggleStatus={onToggleStatus || (() => { })}
     />
    ))}
   </div>
  </div>
 )
}
