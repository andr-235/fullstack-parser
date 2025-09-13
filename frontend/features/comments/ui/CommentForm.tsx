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

import { CommentCreate } from '@/features/comments'

const commentSchema = z.object({
  vk_id: z.number().min(1, 'VK ID обязателен'),
  post_id: z.number().min(1, 'ID поста обязателен'),
  author_id: z.number().min(1, 'ID автора обязателен'),
  text: z
    .string()
    .min(1, 'Содержание комментария обязательно')
    .max(1000, 'Комментарий слишком длинный'),
})

type CommentFormData = z.infer<typeof commentSchema>

interface CommentFormProps {
  initialData?: Partial<CommentCreate>
  onSubmit: (data: CommentCreate) => Promise<void>
  onCancel: () => void
  submitLabel?: string
}

export function CommentForm({
  initialData,
  onSubmit,
  onCancel,
  submitLabel = 'Создать комментарий',
}: CommentFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<CommentFormData>({
    resolver: zodResolver(commentSchema),
    defaultValues: {
      vk_id: initialData?.vk_id || 0,
      post_id: initialData?.post_id || 0,
      author_id: initialData?.author_id || 0,
      text: initialData?.text || '',
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
          name="vk_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>VK ID</FormLabel>
              <FormControl>
                <Input 
                  type="number"
                  placeholder="Введите VK ID комментария..." 
                  {...field}
                  onChange={e => field.onChange(parseInt(e.target.value) || 0)}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="post_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>ID поста</FormLabel>
              <FormControl>
                <Input 
                  type="number"
                  placeholder="Введите ID поста..." 
                  {...field}
                  onChange={e => field.onChange(parseInt(e.target.value) || 0)}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="author_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>ID автора</FormLabel>
              <FormControl>
                <Input 
                  type="number"
                  placeholder="Введите ID автора..." 
                  {...field}
                  onChange={e => field.onChange(parseInt(e.target.value) || 0)}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="text"
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
          <Button type="button" variant="outline" onClick={onCancel} disabled={isSubmitting}>
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
