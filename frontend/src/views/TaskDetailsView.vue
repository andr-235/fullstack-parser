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
          <v-row v-if="task.progress" class="mt-4">
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
      <v-card v-if="task.errors && task.errors.length > 0" class="mb-6" elevation="2">
        <v-card-title class="d-flex align-center">
          <v-icon class="me-2" color="error">mdi-alert-circle</v-icon>
          Ошибки выполнения
          <v-spacer />
          <v-chip color="error" variant="tonal" size="small">
            {{ task.errors.length }}
          </v-chip>
        </v-card-title>
        <v-card-text>
          <v-list>
            <v-list-item
              v-for="(error, index) in task.errors"
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
import { tasksApi } from '@/services/api'
import ResultsTable from '@/components/tasks/ResultsTable.vue'

const route = useRoute()
const router = useRouter()

// Reactive data
const task = ref(null)
const loading = ref(false)
const error = ref('')
const startingTask = ref(false)
const pollingInterval = ref(null)

// Computed
const taskId = computed(() => route.params.taskId)

// Methods
const loadTask = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await tasksApi.getTaskDetails(taskId.value)
    task.value = response.data

    // Start polling if task is in progress
    if (['pending', 'processing'].includes(task.value.status)) {
      startPolling()
    } else {
      stopPolling()
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
    // TODO: Implement start task API call
    console.log('Starting task:', taskId.value)
    await loadTask() // Reload task after starting
  } catch (err) {
    error.value = err.response?.data?.message || err.message || 'Ошибка запуска задачи'
    console.error('Error starting task:', err)
  } finally {
    startingTask.value = false
  }
}

const startPolling = () => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }

  pollingInterval.value = setInterval(async () => {
    try {
      const response = await tasksApi.getTaskDetails(taskId.value)
      task.value = response.data

      // Stop polling if task is completed
      if (['completed', 'failed'].includes(task.value.status)) {
        stopPolling()
      }
    } catch (err) {
      console.error('Error polling task status:', err)
    }
  }, 5000) // Poll every 5 seconds
}

const stopPolling = () => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
    pollingInterval.value = null
  }
}

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
    'vk_collect': 'VK Сбор',
    'groups': 'Группы'
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
  return `${percentage}%`
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
    stopPolling()
    loadTask()
  }
})

// Lifecycle
onMounted(() => {
  loadTask()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
pre {
  font-family: 'Roboto Mono', monospace;
  font-size: 12px;
  line-height: 1.4;
}
</style>