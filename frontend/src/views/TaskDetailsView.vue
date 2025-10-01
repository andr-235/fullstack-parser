<template>
  <v-container fluid class="pa-6">
    <!-- Loading State -->
    <div v-if="loading && !task" class="d-flex justify-center align-center" style="height: 400px">
      <v-progress-circular
        indeterminate
        color="primary"
        size="64"
      />
      <div class="ml-4">
        <h3 class="text-h6">Загрузка задачи...</h3>
        <p class="text-body-2 text-medium-emphasis">Получение информации о задаче</p>
      </div>
    </div>

    <!-- Error State -->
    <v-alert
      v-else-if="error"
      type="error"
      variant="tonal"
      class="mb-6"
    >
      <template #title>
        Ошибка загрузки задачи
      </template>
      {{ error }}
      <template #append>
        <v-btn
          variant="text"
          size="small"
          @click="loadTask"
        >
          Повторить
        </v-btn>
      </template>
    </v-alert>

    <!-- Task Not Found -->
    <div v-else-if="!task" class="text-center pa-8">
      <v-icon size="64" class="mb-4 text-medium-emphasis">
        mdi-file-search-outline
      </v-icon>
      <h3 class="text-h6 mb-2">Задача не найдена</h3>
      <p class="text-body-2 text-medium-emphasis mb-4">
        Задача с ID {{ taskId }} не существует или была удалена
      </p>
      <v-btn
        color="primary"
        to="/tasks"
        prepend-icon="mdi-arrow-left"
      >
        Вернуться к списку задач
      </v-btn>
    </div>

    <!-- Task Details -->
    <div v-else>
      <!-- Header -->
      <div class="d-flex justify-space-between align-start mb-6">
        <div>
          <div class="d-flex align-center mb-2">
            <v-btn
              icon="mdi-arrow-left"
              variant="text"
              size="small"
              class="mr-2"
              @click="$router.push('/tasks')"
            />
            <h1 class="text-h4 font-weight-bold">
              Задача #{{ task.id }}
            </h1>
            <v-chip
              :color="getStatusColor(task.status)"
              variant="flat"
              class="ml-4"
            >
              <v-icon start size="small">
                {{ getStatusIcon(task.status) }}
              </v-icon>
              {{ getStatusText(task.status) }}
            </v-chip>
          </div>
          <p class="text-body-1 text-medium-emphasis">
            {{ getTypeText(task.type) }} • {{ formatDate(task.createdAt) }}
          </p>
        </div>

        <div class="d-flex gap-2">
          <v-btn
            v-if="task.status === 'pending'"
            color="success"
            variant="flat"
            prepend-icon="mdi-play"
            @click="startTask"
            :loading="startingTask"
          >
            Запустить
          </v-btn>
          <v-btn
            variant="outlined"
            prepend-icon="mdi-refresh"
            @click="loadTask"
            :loading="loading"
          >
            Обновить
          </v-btn>
        </div>
      </div>

      <!-- Status Card -->
      <v-card class="mb-6" elevation="2">
        <v-card-title class="d-flex align-center">
          <v-icon class="me-2" color="primary">mdi-information</v-icon>
          Статус задачи
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="3">
              <div class="text-caption text-medium-emphasis">Статус</div>
              <v-chip
                :color="getStatusColor(task.status)"
                variant="flat"
                size="small"
              >
                <v-icon start size="small">
                  {{ getStatusIcon(task.status) }}
                </v-icon>
                {{ getStatusText(task.status) }}
              </v-chip>
            </v-col>
            <v-col cols="12" md="3">
              <div class="text-caption text-medium-emphasis">Приоритет</div>
              <v-chip
                :color="getPriorityColor(task.priority)"
                variant="tonal"
                size="small"
              >
                {{ getPriorityText(task.priority) }}
              </v-chip>
            </v-col>
            <v-col cols="12" md="3">
              <div class="text-caption text-medium-emphasis">Прогресс</div>
              <div class="d-flex align-center">
                <v-progress-linear
                  :model-value="getProgressValue(task)"
                  :color="getProgressColor(task.status)"
                  height="8"
                  rounded
                  class="me-2"
                  style="min-width: 80px"
                />
                <span class="text-body-2">{{ getProgressText(task) }}</span>
              </div>
            </v-col>
            <v-col cols="12" md="3">
              <div class="text-caption text-medium-emphasis">Создана</div>
              <div class="text-body-2">{{ formatDate(task.createdAt) }}</div>
            </v-col>
          </v-row>

          <!-- Progress Metrics -->
          <v-row v-if="task.progress && (task.progress.processed > 0 || task.progress.total > 0)" class="mt-4">
            <v-col cols="12" md="4">
              <v-card variant="tonal" color="info">
                <v-card-text class="text-center py-3">
                  <div class="text-h6 font-weight-bold">{{ task.progress.processed || 0 }}</div>
                  <div class="text-caption">Обработано</div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="4">
              <v-card variant="tonal" color="primary">
                <v-card-text class="text-center py-3">
                  <div class="text-h6 font-weight-bold">{{ task.progress.total || 0 }}</div>
                  <div class="text-caption">Всего</div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="4">
              <v-card variant="tonal" color="success">
                <v-card-text class="text-center py-3">
                  <div class="text-h6 font-weight-bold">{{ getProgressValue(task) }}%</div>
                  <div class="text-caption">Завершено</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Adaptive Polling Status -->
          <v-row v-if="polling.isPolling.value" class="mt-4">
            <v-col cols="12">
              <v-card variant="tonal" color="info">
                <v-card-text class="py-3">
                  <div class="d-flex align-center">
                    <v-icon class="me-2" color="info" size="small">mdi-clock-outline</v-icon>
                    <div class="text-body-2">
                      <strong>Адаптивный polling активен</strong>
                      <div class="text-caption text-medium-emphasis">
                        Интервал: {{ Math.round(polling.currentInterval.value / 1000) }}с
                        <span v-if="polling.retryCount.value > 0">
                          • Попыток с ошибкой: {{ polling.retryCount.value }}
                        </span>
                      </div>
                    </div>
                    <v-spacer />
                    <v-chip
                      :color="polling.lastError.value ? 'warning' : 'success'"
                      variant="tonal"
                      size="small"
                    >
                      {{ polling.lastError.value ? 'С ошибками' : 'Работает' }}
                    </v-chip>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Timestamps -->
          <v-row class="mt-4">
            <v-col cols="12" md="6">
              <div class="text-caption text-medium-emphasis">Обновлена</div>
              <div class="text-body-2">{{ formatDate(task.updatedAt) }}</div>
            </v-col>
            <v-col v-if="task.completedAt" cols="12" md="6">
              <div class="text-caption text-medium-emphasis">Завершена</div>
              <div class="text-body-2">{{ formatDate(task.completedAt) }}</div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Errors List -->
      <v-card v-if="(task.errors && task.errors.length > 0) || task.error" class="mb-6" elevation="2">
        <v-card-title class="d-flex align-center">
          <v-icon class="me-2" color="error">mdi-alert-circle</v-icon>
          Ошибки выполнения
          <v-spacer />
          <v-chip color="error" variant="tonal" size="small">
            {{ (task.errors ? task.errors.length : 0) + (task.error ? 1 : 0) }}
          </v-chip>
        </v-card-title>
        <v-card-text>
          <v-list>
            <!-- Основная ошибка задачи -->
            <v-list-item v-if="task.error">
              <template #prepend>
                <v-icon color="error" size="small">mdi-alert-circle-outline</v-icon>
              </template>
              <v-list-item-title class="text-wrap">
                {{ task.error }}
              </v-list-item-title>
              <v-list-item-subtitle>Основная ошибка</v-list-item-subtitle>
            </v-list-item>

            <!-- Дополнительные ошибки -->
            <v-list-item
              v-for="(error, index) in task.errors || []"
              :key="index"
              :subtitle="error.timestamp ? formatDate(error.timestamp) : undefined"
            >
              <template #prepend>
                <v-icon color="error" size="small">mdi-alert-circle-outline</v-icon>
              </template>
              <v-list-item-title class="text-wrap">
                {{ error.message || error }}
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>

      <!-- Task Result JSON -->
      <v-card v-if="task.result" class="mb-6" elevation="2">
        <v-card-title class="d-flex align-center">
          <v-icon class="me-2" color="success">mdi-code-json</v-icon>
          Результат задачи
          <v-spacer />
          <v-btn
            variant="text"
            size="small"
            prepend-icon="mdi-download"
            @click="downloadResult"
          >
            Скачать JSON
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-expansion-panels variant="accordion">
            <v-expansion-panel>
              <v-expansion-panel-title>
                Показать JSON данные
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <pre class="text-caption bg-grey-lighten-5 pa-3 rounded" style="overflow: auto; max-height: 400px">{{ JSON.stringify(task.result, null, 2) }}</pre>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-card-text>
      </v-card>

      <!-- Results Table -->
      <ResultsTable
        v-if="task.status === 'completed'"
        :task-id="taskId"
        class="mb-6"
      />
    </div>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { tasksApi, postStartCollect } from '@/services/api'
import { useAdaptivePolling } from '@/composables/useAdaptivePolling'
import ResultsTable from '@/components/tasks/ResultsTable.vue'

const route = useRoute()
const router = useRouter()

// Reactive data
const task = ref(null)
const loading = ref(false)
const error = ref('')
const startingTask = ref(false)

// Computed
const taskId = computed(() => route.params.taskId)

// Адаптивный polling
const polling = useAdaptivePolling(
  computed(() => String(taskId.value)),
  'general' // Для детального просмотра задач используем general конфиг
)

// Methods
const loadTask = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await tasksApi.getTaskDetails(taskId.value)
    task.value = response.data

    console.log('Загружена задача:', {
      taskId: taskId.value,
      status: task.value.status,
      progress: task.value.progress,
      data: task.value
    })

    // Запускаем адаптивный polling если задача выполняется
    if (['pending', 'processing'].includes(task.value.status)) {
      console.log('Запускаем polling для задачи:', taskId.value)
      await polling.startPolling(async () => {
        const statusResponse = await tasksApi.getTaskDetails(taskId.value)
        // Обновляем данные задачи из response
        const oldStatus = task.value.status
        const oldProgress = task.value.progress
        task.value = statusResponse.data

        console.log('Polling обновление:', {
          taskId: taskId.value,
          oldStatus,
          newStatus: statusResponse.data.status,
          oldProgress,
          newProgress: statusResponse.data.progress,
          data: statusResponse.data
        })

        return {
          status: statusResponse.data.status,
          progress: statusResponse.data.progress,
          ...statusResponse.data
        }
      })
    } else {
      console.log('Не запускаем polling, статус:', task.value.status)
      polling.stopPolling()
    }
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = 'Задача не найдена'
    } else {
      error.value = err.response?.data?.message || err.message || 'Ошибка загрузки задачи'
    }
    console.error('Error loading task:', err)
  } finally {
    loading.value = false
  }
}

const startTask = async () => {
  if (!task.value || task.value.status !== 'pending') return

  startingTask.value = true

  try {
    console.log('Запуск задачи:', taskId.value)
    // Используем API для запуска задачи
    await postStartCollect(taskId.value)
    console.log('Задача запущена успешно')
    await loadTask() // Перезагружаем задачу после запуска
  } catch (err) {
    error.value = err.response?.data?.message || err.message || 'Ошибка запуска задачи'
    console.error('Ошибка запуска задачи:', err)
  } finally {
    startingTask.value = false
  }
}

// Методы polling теперь управляются через useAdaptivePolling composable
// polling.startPolling() и polling.stopPolling() вызываются автоматически

const downloadResult = () => {
  if (!task.value?.result) return

  const dataStr = JSON.stringify(task.value.result, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)

  const exportFileDefaultName = `task_${task.value.id}_result.json`

  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
}

// Helper functions
const getStatusColor = (status) => {
  const colors = {
    'pending': 'orange',
    'processing': 'blue',
    'completed': 'green',
    'failed': 'red'
  }
  return colors[status] || 'grey'
}

const getStatusIcon = (status) => {
  const icons = {
    'pending': 'mdi-clock-outline',
    'processing': 'mdi-loading',
    'completed': 'mdi-check-circle',
    'failed': 'mdi-alert-circle'
  }
  return icons[status] || 'mdi-help'
}

const getStatusText = (status) => {
  const texts = {
    'pending': 'Ожидает',
    'processing': 'В процессе',
    'completed': 'Завершена',
    'failed': 'Ошибка'
  }
  return texts[status] || status
}

const getTypeText = (type) => {
  const texts = {
    'comments': 'Комментарии',
    'fetch_comments': 'Сбор комментариев',
    'vk_collect': 'VK Сбор',
    'groups': 'Группы',
    'process_groups': 'Обработка групп'
  }
  return texts[type] || type
}

const getPriorityColor = (priority) => {
  const colors = {
    'low': 'green',
    'normal': 'blue',
    'high': 'orange',
    'critical': 'red'
  }
  return colors[priority] || 'grey'
}

const getPriorityText = (priority) => {
  const texts = {
    'low': 'Низкий',
    'normal': 'Обычный',
    'high': 'Высокий',
    'critical': 'Критичный'
  }
  return texts[priority] || priority || 'Обычный'
}

const getProgressValue = (task) => {
  if (!task.progress) return 0
  if (task.status === 'completed') return 100
  if (task.status === 'failed') return 0

  const { processed = 0, total = 0 } = task.progress
  return total > 0 ? Math.round((processed / total) * 100) : 0
}

const getProgressColor = (status) => {
  const colors = {
    'pending': 'grey',
    'processing': 'primary',
    'completed': 'success',
    'failed': 'error'
  }
  return colors[status] || 'grey'
}

const getProgressText = (task) => {
  if (!task.progress) return '0%'
  if (task.status === 'completed') return '100%'
  if (task.status === 'failed') return 'Ошибка'

  const { processed = 0, total = 0 } = task.progress
  if (total === 0) return '0%'

  const percentage = Math.round((processed / total) * 100)
  return `${processed}/${total} (${percentage}%)`
}

const formatDate = (dateString) => {
  if (!dateString) return '-'

  const date = new Date(dateString)
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

// Watch for route changes
watch(() => route.params.taskId, (newTaskId) => {
  if (newTaskId) {
    polling.stopPolling()
    loadTask()
  }
})

// Lifecycle
onMounted(() => {
  loadTask()
})

onUnmounted(() => {
  polling.stopPolling()
})
</script>

<style scoped>
pre {
  font-family: 'Roboto Mono', monospace;
  font-size: 12px;
  line-height: 1.4;
}
</style>