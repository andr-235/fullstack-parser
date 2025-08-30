'use client'

import { useState } from 'react'
import { Button } from '@/shared/ui'
import { Card, CardContent } from '@/shared/ui'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Textarea } from '@/shared/ui'
import { Switch } from '@/shared/ui'
import { Label } from '@/shared/ui'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

const groupSchema = z.object({
 vk_id_or_screen_name: z.string().min(1, 'VK ID или screen name обязателен'),
 name: z.string().optional(),
 screen_name: z.string().optional(),
 description: z.string().optional(),
 is_active: z.boolean().optional(),
 max_posts_to_check: z.number().min(1).max(10000).optional(),
})

type GroupFormData = z.infer<typeof groupSchema>

interface GroupFormProps {
 initialData?: Partial<GroupFormData>
 onSubmit: (data: GroupFormData) => Promise<void>
 onCancel: () => void
 submitLabel?: string
}

export function GroupForm({
 initialData,
 onSubmit,
 onCancel,
 submitLabel = 'Создать группу'
}: GroupFormProps) {
 const [isSubmitting, setIsSubmitting] = useState(false)

 const form = useForm<GroupFormData>({
  resolver: zodResolver(groupSchema),
  defaultValues: {
   vk_id_or_screen_name: initialData?.vk_id_or_screen_name || '',
   name: initialData?.name || '',
   screen_name: initialData?.screen_name || '',
   description: initialData?.description || '',
   is_active: initialData?.is_active,
   max_posts_to_check: initialData?.max_posts_to_check,
  },
 })

 const handleSubmit = async (data: GroupFormData) => {
  setIsSubmitting(true)
  try {
   await onSubmit(data)
   form.reset()
  } catch (error) {
   console.error('Form submission error:', error)
  } finally {
   setIsSubmitting(false)
  }
 }

 return (
  <Form {...form}>
   <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
    <FormField
     control={form.control}
     name="vk_id_or_screen_name"
     render={({ field }) => (
      <FormItem>
       <FormLabel>ID группы VK или Screen Name</FormLabel>
       <FormControl>
        <Input
         placeholder="Введите ID группы (например 12345) или screen name (например @group_name)"
         {...field}
        />
       </FormControl>
       <FormMessage />
      </FormItem>
     )}
    />

    <FormField
     control={form.control}
     name="name"
     render={({ field }) => (
      <FormItem>
       <FormLabel>Название группы (необязательно)</FormLabel>
       <FormControl>
        <Input
         placeholder="Название группы будет получено из VK API"
         {...field}
        />
       </FormControl>
       <FormMessage />
      </FormItem>
     )}
    />

    <FormField
     control={form.control}
     name="screen_name"
     render={({ field }) => (
      <FormItem>
       <FormLabel>Screen Name (необязательно)</FormLabel>
       <FormControl>
        <Input
         placeholder="Screen name будет получено из VK API"
         {...field}
        />
       </FormControl>
       <FormMessage />
      </FormItem>
     )}
    />

    <FormField
     control={form.control}
     name="description"
     render={({ field }) => (
      <FormItem>
       <FormLabel>Описание (необязательно)</FormLabel>
       <FormControl>
        <Textarea
         placeholder="Описание группы"
         className="min-h-[80px]"
         {...field}
        />
       </FormControl>
       <FormMessage />
      </FormItem>
     )}
    />

    <FormField
     control={form.control}
     name="max_posts_to_check"
     render={({ field }) => (
      <FormItem>
       <FormLabel>Максимальное количество постов для проверки</FormLabel>
       <FormControl>
        <Input
         type="number"
         min={1}
         max={10000}
         {...field}
         onChange={(e) => field.onChange(parseInt(e.target.value) || undefined)}
        />
       </FormControl>
       <FormMessage />
      </FormItem>
     )}
    />

    <FormField
     control={form.control}
     name="is_active"
     render={({ field }) => (
      <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
       <div className="space-y-0.5">
        <FormLabel className="text-base">Активный мониторинг</FormLabel>
        <div className="text-sm text-muted-foreground">
         Включить мониторинг комментариев для этой группы
        </div>
       </div>
       <FormControl>
        <Switch
         checked={field.value ?? true}
         onCheckedChange={field.onChange}
        />
       </FormControl>
      </FormItem>
     )}
    />

    <div className="flex justify-end gap-2 pt-4">
     <Button
      type="button"
      variant="outline"
      onClick={onCancel}
      disabled={isSubmitting}
     >
      Отмена
     </Button>
     <Button type="submit" disabled={isSubmitting}>
      {isSubmitting ? 'Сохранение...' : submitLabel}
     </Button>
    </div>
   </form>
  </Form>
 )
}
