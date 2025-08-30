'use client'

import { useState } from 'react'
import { Button } from '@/shared/ui'
import { Card, CardContent } from '@/shared/ui'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Textarea } from '@/shared/ui'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui'
import { Switch } from '@/shared/ui'
import { Label } from '@/shared/ui'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { KEYWORD_CATEGORIES } from '@/entities/keywords'

const keywordSchema = z.object({
 word: z.string().min(1, 'Keyword is required').max(200, 'Keyword is too long'),
 category: z.string().optional(),
 description: z.string().optional(),
 is_active: z.boolean().optional(),
 is_case_sensitive: z.boolean().optional(),
 is_whole_word: z.boolean().optional(),
})

type KeywordFormData = z.infer<typeof keywordSchema>

interface KeywordFormProps {
 initialData?: Partial<KeywordFormData>
 onSubmit: (data: KeywordFormData) => Promise<void>
 onCancel: () => void
 submitLabel?: string
}

export function KeywordForm({
 initialData,
 onSubmit,
 onCancel,
 submitLabel = 'Create Keyword'
}: KeywordFormProps) {
 const [isSubmitting, setIsSubmitting] = useState(false)

 const form = useForm<KeywordFormData>({
  resolver: zodResolver(keywordSchema),
  defaultValues: {
   word: initialData?.word || '',
   category: initialData?.category || '',
   description: initialData?.description || '',
   is_active: initialData?.is_active ?? true,
   is_case_sensitive: initialData?.is_case_sensitive ?? false,
   is_whole_word: initialData?.is_whole_word ?? false,
  },
 })

 const handleSubmit = async (data: KeywordFormData) => {
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
     name="word"
     render={({ field }) => (
      <FormItem>
       <FormLabel>Ключевое слово</FormLabel>
       <FormControl>
        <Input
         placeholder="Введите ключевое слово для мониторинга..."
         {...field}
        />
       </FormControl>
       <FormMessage />
      </FormItem>
     )}
    />

    <FormField
     control={form.control}
     name="category"
     render={({ field }) => (
      <FormItem>
       <FormLabel>Категория (необязательно)</FormLabel>
       <Select onValueChange={field.onChange} value={field.value || ''}>
        <FormControl>
         <SelectTrigger>
          <SelectValue placeholder="Выберите категорию" />
         </SelectTrigger>
        </FormControl>
        <SelectContent>
         {KEYWORD_CATEGORIES.map((category) => (
          <SelectItem key={category.key} value={category.key}>
           {category.label}
          </SelectItem>
         ))}
        </SelectContent>
       </Select>
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
         placeholder="Опишите, для чего предназначено это ключевое слово..."
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
     name="is_active"
     render={({ field }) => (
      <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
       <div className="space-y-0.5">
        <FormLabel className="text-base">Активный мониторинг</FormLabel>
        <div className="text-sm text-muted-foreground">
         Включить мониторинг комментариев для этого ключевого слова
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

    <FormField
     control={form.control}
     name="is_case_sensitive"
     render={({ field }) => (
      <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
       <div className="space-y-0.5">
        <FormLabel className="text-base">Регистр</FormLabel>
        <div className="text-sm text-muted-foreground">
         Совпадение с точным регистром
        </div>
       </div>
       <FormControl>
        <Switch
         checked={field.value ?? false}
         onCheckedChange={field.onChange}
        />
       </FormControl>
      </FormItem>
     )}
    />

    <FormField
     control={form.control}
     name="is_whole_word"
     render={({ field }) => (
      <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
       <div className="space-y-0.5">
        <FormLabel className="text-base">Только целое слово</FormLabel>
        <div className="text-sm text-muted-foreground">
         Совпадение только с целыми словами
        </div>
       </div>
       <FormControl>
        <Switch
         checked={field.value ?? false}
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
