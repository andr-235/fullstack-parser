import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { getComments } from "@/services/api";

/**
 * Pinia store для управления комментариями.
 */
export const useCommentsStore = defineStore("comments", () => {
  /**
   * Список комментариев.
   */
  const list = ref([]);

  /**
   * Статус загрузки.
   */
  const loading = ref(false);

  /**
   * Ошибка.
   */
  const error = ref(null);

  /**
   * Фильтры.
   */
  const filters = ref({
    sentiment: null,
    keyword: ""
  });

  /**
   * Пагинация.
   */
  const pagination = ref({
    currentPage: 1,
    itemsPerPage: 20,
    total: 0
  });

  /**
   * Загружает комментарии для задачи с фильтрами и пагинацией.
   * @param {number} taskId - ID задачи.
   * @param {Object} [filtersData={}] - Фильтры (sentiment, keyword).
   * @param {number} [page=1] - Номер страницы.
   * @returns {Promise<void>}
   * @throws {Error} При ошибке загрузки.
   * @example
   * await fetchComments(1, { sentiment: "positive", keyword: "test" }, 1);
   */
  const fetchComments = async (taskId, filtersData = {}, page = 1) => {
    loading.value = true;
    error.value = null;
    try {
      pagination.value.currentPage = page;
      const params = {
        ...filtersData,
        page,
        limit: pagination.value.itemsPerPage
      };
      const data = await getComments(taskId, params);
      list.value = data.comments;
      pagination.value.total = data.total;
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Getter для отфильтрованных комментариев (client-side фильтрация).
   */
  const filteredComments = computed(() => {
    let result = list.value;
    if (filters.value.sentiment) {
      result = result.filter(comment => comment.sentiment === filters.value.sentiment);
    }
    if (filters.value.keyword) {
      const keyword = filters.value.keyword.toLowerCase();
      result = result.filter(comment => comment.text.toLowerCase().includes(keyword));
    }
    return result;
  });

  /**
   * Getter для пагинированных комментариев (client-side срез).
   */
  const paginatedComments = computed(() => {
    const start = (pagination.value.currentPage - 1) * pagination.value.itemsPerPage;
    const end = start + pagination.value.itemsPerPage;
    return filteredComments.value.slice(start, end);
  });

  return {
    list,
    loading,
    error,
    filters,
    pagination,
    fetchComments,
    filteredComments,
    paginatedComments
  };
});