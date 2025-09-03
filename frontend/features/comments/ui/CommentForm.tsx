'use client'

import { useState } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import * as z from 'zod'

import { Button } from '@/shared/ui'
import { Card, CardContent } from '@/shared/ui'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Textarea } from '@/shared/ui'

const commentSchema = z.object({
 content: z.string().min(1, 'Содержание комментария обязательно').max(1000, 'Комментарий слишком длинный'),
 postId: z.string().min(1, 'ID поста обязателен'),
})

type CommentFormData = z.infer<typeof commentSchema>

interface CommentFormProps {
 initialData?: {
  content?: string
  postId?: string
 }
 onSubmit: (data: CommentFormData) => Promise<void>
 onCancel: () => void
 submitLabel?: string
}

export function CommentForm({
 initialData,
 onSubmit,
 onCancel,
 submitLabel = 'Создать комментарий'
}: CommentFormProps) {
 const [isSubmitting, setIsSubmitting] = useState(false)

 const form = useForm<CommentFormData>({
  resolver: zodResolver(commentSchema),
  defaultValues: {
   content: initialData?.content || '',
   postId: initialData?.postId || '',
  },
 })

 const handleSubmit = async (data: CommentFormData) => {
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
     name="postId"
     render={({ field }) => (
      <FormItem>
       <FormLabel>ID поста</FormLabel>
       <FormControl>
        <Input
         placeholder="Введите ID поста..."
         {...field}
        />
       </FormControl>
       <FormMessage />
      </FormItem>
     )}
    />

    <FormField
     control={form.control}
     name="content"
     render={({ field }) => (
      <FormItem>
       <FormLabel>Содержание комментария</FormLabel>
       <FormControl>
        <Textarea
         placeholder="Напишите ваш комментарий здесь..."
         className="min-h-[100px]"
         {...field}
        />
       </FormControl>
       <FormMessage />
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
