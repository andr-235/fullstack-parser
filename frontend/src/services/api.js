import axios from "axios";

const apiUrl = import.meta.env.MODE === 'production' ? '' : (import.meta.env.VITE_API_BASE || 'http://localhost:3000');
const api = axios.create({
  baseURL: apiUrl
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 429 && !originalRequest._retry) {
      originalRequest._retry = true;
      const retryCount = originalRequest.retryCount || 0;
      if (retryCount < 3) {
        originalRequest.retryCount = retryCount + 1;
        const delay = Math.pow(2, retryCount) * 1000;
        await new Promise((resolve) => setTimeout(resolve, delay));
        return api(originalRequest);
      }
    }
    if (error.response && [400, 500].includes(error.response.status)) {
      console.error("API Error:", error.response.data || error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * Создает новую задачу сбора комментариев.
 * @param {Object} data - Данные: {ownerId, postId, token}
 * @returns {Promise<Object>} Ответ с taskId
 */
export const postCreateTask = async (data) => {
  return api.post("/tasks", data);
};

/**
 * Запускает сбор данных для задачи.
 * @param {string|number} taskId - ID задачи
 * @returns {Promise<Object>} Ответ с taskId и status
 */
export const postStartCollect = async (taskId) => {
  return api.post(`/collect/${taskId}`);
};

/**
 * Получает статус задачи.
 * @param {string|number} taskId - ID задачи
 * @returns {Promise<Object>} {status, progress, errors}
 */
export const getTaskStatus = async (taskId) => {
  return api.get(`/tasks/${taskId}`);
};

/**
 * Получает результаты комментариев.
 * @param {string|number} taskId - ID задачи
 * @param {Object} [params={}] - Параметры: groupId, postId, sentiment, limit, offset
 * @returns {Promise<Object>} {results: [...], total}
 */
export const getResults = async (taskId, params = {}) => {
  const defaultParams = {
    limit: 20,
    offset: 0,
    ...params
  };
  return api.get(`/results/${taskId}`, { params: defaultParams });
};

// Tasks API
export const tasksApi = {
  /**
   * Получает список задач с пагинацией.
   * @param {Object} [params={}] - Параметры: page, limit, status
   * @returns {Promise<Object>} {tasks: [...], total, page, totalPages}
   */
  getTasks: (params = {}) =>
    api.get('/tasks', { params }),

  /**
   * Создает новую VK collect задачу.
   * @param {Object} data - Данные: {groups: number[], token: string}
   * @returns {Promise<Object>} Ответ с taskId
   */
  createVkCollectTask: (data) =>
    api.post('/tasks/collect', data),

  /**
   * Получает детальную информацию о задаче.
   * @param {string|number} taskId - ID задачи
   * @returns {Promise<Object>} Детальная информация о задаче
   */
  getTaskDetails: (taskId) =>
    api.get(`/tasks/${taskId}`)
};

// Groups API
export const groupsApi = {
  /**
   * Загружает файл с группами VK.
   * @param {FormData} formData - Данные формы с файлом
   * @param {string} encoding - Кодировка файла
   * @returns {Promise<Object>} Ответ с taskId
   */
  uploadGroups: (formData, encoding = 'utf-8') => 
    api.post('/groups/upload', formData, { 
      headers: { 'Content-Type': 'multipart/form-data' },
      params: { encoding }
    }),
  
  /**
   * Получает статус задачи загрузки групп.
   * @param {string|number} taskId - ID задачи
   * @returns {Promise<Object>} {status, progress, errors}
   */
  getTaskStatus: (taskId) => 
    api.get(`/groups/upload/${taskId}/status`),
  
  /**
   * Получает список групп.
   * @param {Object} [params={}] - Параметры: page, limit, status, search, sortBy, sortOrder
   * @returns {Promise<Object>} {groups: [...], total}
   */
  getGroups: (params = {}) => 
    api.get('/groups', { params }),
  
  /**
   * Удаляет группу.
   * @param {string|number} groupId - ID группы
   * @returns {Promise<Object>} Ответ сервера
   */
  deleteGroup: (groupId) => 
    api.delete(`/groups/${groupId}`),
  
  /**
   * Массовое удаление групп.
   * @param {Array} groupIds - Массив ID групп
   * @returns {Promise<Object>} Ответ сервера
   */
  deleteGroups: (groupIds) => 
    api.delete('/groups/batch', { data: { groupIds }})
};