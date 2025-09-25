import { defineStore } from "pinia";
import { ref } from "vue";
import { postCreateTask, postStartCollect, getTaskStatus } from "@/services/api";

export const useTasksStore = defineStore("tasks", () => {
  const taskId = ref(null);
  const status = ref("");
  const progress = ref({ posts: 0, comments: 0 });
  const errors = ref([]);
  const intervalId = ref(null);

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

  return {
    taskId,
    status,
    progress,
    errors,
    createTask,
    startCollect,
    pollStatus,
    stopPolling
  };
});