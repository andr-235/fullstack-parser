import { defineStore } from "pinia";
import { ref } from "vue";
import { getResults } from "@/services/api";

export const useCommentsStore = defineStore("comments", () => {
  const results = ref([]);
  const total = ref(0);
  const currentTaskId = ref(null);
  const filters = ref({
    groupId: null,
    postId: null,
    sentiment: ""
  });
  const pagination = ref({
    limit: 20,
    offset: 0
  });

  /**
   * Загружает комментарии с фильтрами и пагинацией.
   * @param {string|number} taskId - ID задачи
   * @param {Object} [filters={}] - Фильтры: groupId, postId, sentiment
   * @returns {Promise<void>}
   */
  const fetchComments = async (taskId, filtersParam = {}) => {
    currentTaskId.value = taskId;
    const mergedFilters = {
      ...filters.value,
      ...filtersParam
    };
    const params = {
      ...mergedFilters,
      ...pagination.value
    };
    try {
      const response = await getResults(taskId, params);
      results.value = response.data.results || [];
      total.value = response.data.total || 0;
    } catch (error) {
      console.error("Ошибка загрузки комментариев:", error);
      results.value = [];
      total.value = 0;
    }
  };

  /**
   * Обновляет фильтры и сбрасывает пагинацию.
   * @param {Object} newFilters - Новые фильтры
   * @returns {void}
   */
  const updateFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters };
    pagination.value.offset = 0;
    if (currentTaskId.value) {
      fetchComments(currentTaskId.value);
    }
  };

  /**
   * Обновляет пагинацию и загружает данные.
   * @param {number} newOffset - Новый offset
   * @returns {void}
   */
  const updatePagination = (newOffset) => {
    pagination.value.offset = newOffset;
    if (currentTaskId.value) {
      fetchComments(currentTaskId.value);
    }
  };

  return {
    results,
    total,
    filters,
    pagination,
    currentTaskId,
    fetchComments,
    updateFilters,
    updatePagination
  };
});