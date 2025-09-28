import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getResults } from '@/services/api'
import type { Comment } from '@/types/api'

interface CommentFilters {
  groupId: string | number | null
  postId: string | number | null
  sentiment: string
}

interface CommentPagination {
  limit: number
  offset: number
}

export const useCommentsStore = defineStore('comments', () => {
  const results = ref<Comment[]>([])
  const total = ref<number>(0)
  const currentTaskId = ref<string | number | null>(null)
  const filters = ref<CommentFilters>({
    groupId: null,
    postId: null,
    sentiment: ''
  })
  const pagination = ref<CommentPagination>({
    limit: 20,
    offset: 0
  })

  /**
   * Загружает комментарии с фильтрами и пагинацией.
   */
  const fetchComments = async (taskId: string | number, filtersParam: Partial<CommentFilters> = {}): Promise<void> => {
    currentTaskId.value = taskId
    const mergedFilters = {
      ...filters.value,
      ...filtersParam
    }
    const params = {
      ...mergedFilters,
      ...pagination.value
    }
    try {
      const response = await getResults(taskId, params)
      const responseData = response.data.data || response.data
      results.value = responseData.results || []
      total.value = responseData.total || 0
    } catch (error) {
      console.error('Ошибка загрузки комментариев:', error)
      results.value = []
      total.value = 0
    }
  }

  /**
   * Обновляет фильтры и сбрасывает пагинацию.
   */
  const updateFilters = (newFilters: Partial<CommentFilters>): void => {
    filters.value = { ...filters.value, ...newFilters }
    pagination.value.offset = 0
    if (currentTaskId.value) {
      fetchComments(currentTaskId.value)
    }
  }

  /**
   * Обновляет пагинацию и загружает данные.
   */
  const updatePagination = (newOffset: number): void => {
    pagination.value.offset = newOffset
    if (currentTaskId.value) {
      fetchComments(currentTaskId.value)
    }
  }

  return {
    results,
    total,
    filters,
    pagination,
    currentTaskId,
    fetchComments,
    updateFilters,
    updatePagination
  }
})