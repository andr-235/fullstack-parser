import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { postCreateTask, postStartCollect, getTaskStatus, tasksApi } from "@/services/api";

export const useTasksStore = defineStore("tasks", () => {
  // Single task state (existing)
  const taskId = ref(null);
  const status = ref("");
  const progress = ref({ posts: 0, comments: 0 });
  const errors = ref([]);
  const intervalId = ref(null);

  // Tasks list state (new)
  const tasks = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const pagination = ref({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0
  });
  const filters = ref({
    status: ''
  });

  /**
   * Создает новую задачу.
   * @param {Object} data - {ownerId, postId, token}
   * @returns {Promise<void>}
   */
  const createTask = async (data) => {
    try {
      const response = await postCreateTask(data);
      taskId.value = response.data.taskId;
      status.value = "created";
      errors.value = [];
    } catch (error) {
      errors.value.push(error.message);
      throw error;
    }
  };

  /**
   * Запускает сбор данных и polling статуса.
   * @returns {Promise<void>}
   */
  const startCollect = async () => {
    if (!taskId.value) {
      throw new Error("Task ID не установлен");
    }
    try {
      await postStartCollect(taskId.value);
      status.value = "pending";
      pollStatus();
    } catch (error) {
      errors.value.push(error.message);
      throw error;
    }
  };

  /**
   * Поллинг статуса задачи каждые 5 секунд.
   * @returns {void}
   */
  const pollStatus = () => {
    if (intervalId.value) {
      clearInterval(intervalId.value);
    }
    intervalId.value = setInterval(async () => {
      try {
        const response = await getTaskStatus(taskId.value);
        status.value = response.data.status;
        progress.value = response.data.progress;
        errors.value = response.data.errors || [];
        if (["completed", "failed"].includes(status.value)) {
          clearInterval(intervalId.value);
          intervalId.value = null;
        }
      } catch (error) {
        errors.value.push(error.message);
      }
    }, 5000);
  };

  /**
   * Останавливает polling.
   * @returns {void}
   */
  const stopPolling = () => {
    if (intervalId.value) {
      clearInterval(intervalId.value);
      intervalId.value = null;
    }
  };

  // Tasks list actions

  /**
   * Загружает список задач с пагинацией и фильтрацией.
   * @returns {Promise<void>}
   */
  const fetchTasks = async () => {
    loading.value = true;
    error.value = null;

    try {
      const params = {
        page: pagination.value.page,
        limit: pagination.value.limit,
        ...(filters.value.status && { status: filters.value.status })
      };

      const response = await tasksApi.getTasks(params);
      const data = response.data;

      tasks.value = data.tasks || [];
      pagination.value = {
        ...pagination.value,
        total: data.total || 0,
        totalPages: data.totalPages || 0
      };
    } catch (err) {
      error.value = err.response?.data?.message || err.message || 'Ошибка загрузки задач';
      console.error('Error fetching tasks:', err);
    } finally {
      loading.value = false;
    }
  };

  /**
   * Создает новую VK collect задачу.
   * @param {Object} data - {groups: number[], token: string}
   * @returns {Promise<Object>} Ответ с taskId
   */
  const createVkCollectTask = async (data) => {
    try {
      const response = await tasksApi.createVkCollectTask(data);
      await fetchTasks(); // Обновляем список задач
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.message || err.message || 'Ошибка создания задачи';
      error.value = errorMessage;
      throw new Error(errorMessage);
    }
  };

  /**
   * Устанавливает страницу пагинации.
   * @param {number} page - Номер страницы
   */
  const setPage = (page) => {
    pagination.value.page = page;
  };

  /**
   * Устанавливает фильтр по статусу.
   * @param {string} statusFilter - Статус для фильтрации
   */
  const setStatusFilter = (statusFilter) => {
    filters.value.status = statusFilter;
    pagination.value.page = 1; // Сбрасываем на первую страницу при изменении фильтра
  };

  // Computed properties
  const hasNextPage = computed(() =>
    pagination.value.page < pagination.value.totalPages
  );

  const hasPrevPage = computed(() =>
    pagination.value.page > 1
  );

  const isEmpty = computed(() =>
    !loading.value && tasks.value.length === 0
  );

  return {
    // Single task state
    taskId,
    status,
    progress,
    errors,
    createTask,
    startCollect,
    pollStatus,
    stopPolling,

    // Tasks list state
    tasks,
    loading,
    error,
    pagination,
    filters,

    // Tasks list actions
    fetchTasks,
    createVkCollectTask,
    setPage,
    setStatusFilter,

    // Computed properties
    hasNextPage,
    hasPrevPage,
    isEmpty
  };
});