import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { postTask, getTaskStatus } from "@/services/api";

/**
 * Pinia store для управления задачами.
 */
export const useTasksStore = defineStore("tasks", () => {
  /**
   * Текущее состояние задачи.
   */
  const currentTask = ref({
    id: null,
    status: null,
    progress: 0,
    error: null
  });

  /**
   * Создает новую задачу и обновляет состояние.
   * @param {Object} data - Данные для создания задачи.
   * @param {number} data.ownerId - ID владельца поста.
   * @param {number} data.postId - ID поста.
   * @param {string} data.access_token - Токен доступа VK.
   * @returns {Promise<void>}
   * @throws {Error} При ошибке создания задачи.
   * @example
   * await createTask({ ownerId: 1, postId: 1, access_token: "token" });
   */
  const createTask = async (data) => {
    try {
      currentTask.value.id = await postTask(data);
      currentTask.value.status = "pending";
      currentTask.value.progress = 0;
      currentTask.value.error = null;
    } catch (err) {
      currentTask.value.error = err.message;
      throw err;
    }
  };

  /**
   * Получает и обновляет статус задачи.
   * @param {number} taskId - ID задачи.
   * @returns {Promise<void>}
   * @throws {Error} При ошибке получения статуса.
   * @example
   * await fetchStatus(1);
   */
  const fetchStatus = async (taskId) => {
    try {
      const data = await getTaskStatus(taskId);
      currentTask.value.status = data.status;
      currentTask.value.progress = data.progress;
      currentTask.value.error = null;
    } catch (err) {
      currentTask.value.error = err.message;
    }
  };

  /**
   * Getter для отформатированного статуса на русском языке.
   */
  const getFormattedStatus = computed(() => {
    const statusMap = {
      "pending": "Ожидание",
      "processing": "В обработке",
      "completed": "Завершено",
      "error": "Ошибка"
    };
    return statusMap[currentTask.value.status] || currentTask.value.status;
  });

  return {
    currentTask,
    createTask,
    fetchStatus,
    getFormattedStatus
  };
});