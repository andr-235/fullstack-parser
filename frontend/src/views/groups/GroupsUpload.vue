<template>
  <v-container fluid class="pa-6">
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold">Загрузка групп</h1>
        <p class="text-body-1 text-medium-emphasis mt-1">
          Загрузка и обработка файлов с ID групп VK
        </p>
      </div>
    </div>

    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <GroupsUploadForm @upload-started="onUploadStarted" />

        <!-- Task Status Card -->
        <v-card v-if="uploadTask.taskId" class="mt-6" elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="me-2" color="primary">mdi-progress-check</v-icon>
            Обработка файла
            <v-spacer />
            <v-chip
              :color="getStatusColor(uploadTask.status)"
              variant="flat"
              size="small"
            >
              <v-icon start size="small">
                {{ getStatusIcon(uploadTask.status) }}
              </v-icon>
              {{ getStatusText(uploadTask.status) }}
            </v-chip>
          </v-card-title>

          <v-card-text>
            <!-- Task ID -->
            <div class="mb-4">
              <div class="text-caption text-medium-emphasis">Task ID</div>
              <v-chip color="primary" variant="tonal" size="small">
                {{ uploadTask.taskId }}
              </v-chip>
            </div>

            <!-- Progress Bar -->
            <div v-if="uploadTask.progress" class="mb-4">
              <div class="d-flex justify-space-between align-center mb-2">
                <span class="text-body-2 font-weight-medium">Прогресс обработки</span>
                <span class="text-body-2">
                  {{ uploadTask.progress.processed || 0 }}/{{ uploadTask.progress.total || 0 }}
                  ({{ getProgressPercentage() }}%)
                </span>
              </div>
              <v-progress-linear
                :model-value="getProgressPercentage()"
                :color="getProgressColor(uploadTask.status)"
                height="8"
                rounded
              />
            </div>

            <!-- Status Message -->
            <div v-if="uploadTask.message" class="mb-4">
              <v-alert
                :type="getMessageType(uploadTask.status)"
                variant="tonal"
                density="compact"
                :text="uploadTask.message"
              />
            </div>

            <!-- Success message with redirect countdown -->
            <div v-if="uploadTask.status === 'completed' && redirectCountdown > 0" class="mb-4">
              <v-alert
                type="success"
                variant="tonal"
                density="compact"
              >
                <div class="d-flex justify-space-between align-center">
                  <div class="d-flex align-center">
                    <v-icon class="me-2">mdi-check-circle</v-icon>
                    <span>Файл успешно обработан! Переход к списку групп через {{ redirectCountdown }} сек...</span>
                  </div>
                  <v-btn
                    variant="text"
                    size="small"
                    @click="stopRedirectCountdown"
                  >
                    Отменить
                  </v-btn>
                </div>
              </v-alert>
            </div>

            <!-- Action Buttons -->
            <div class="d-flex gap-2">
              <v-btn
                variant="outlined"
                size="small"
                prepend-icon="mdi-refresh"
                @click="refreshStatus"
                :loading="refreshing"
              >
                Обновить статус
              </v-btn>

              <v-btn
                v-if="uploadTask.status === 'completed'"
                color="success"
                variant="flat"
                size="small"
                prepend-icon="mdi-eye"
                :to="`/groups`"
              >
                Просмотреть группы
              </v-btn>

              <v-btn
                v-if="uploadTask.errors && uploadTask.errors.length > 0"
                color="warning"
                variant="outlined"
                size="small"
                prepend-icon="mdi-download"
                @click="downloadErrorReport"
              >
                Скачать отчёт об ошибках
              </v-btn>
            </div>
          </v-card-text>
        </v-card>

        <!-- Errors List -->
        <v-card v-if="uploadTask.errors && uploadTask.errors.length > 0" class="mt-6" elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="me-2" color="error">mdi-alert-circle</v-icon>
            Ошибки парсинга
            <v-spacer />
            <v-chip color="error" variant="tonal" size="small">
              {{ uploadTask.errors.length }}
            </v-chip>
          </v-card-title>

          <v-card-text>
            <v-list density="compact" max-height="300" class="overflow-y-auto">
              <v-list-item
                v-for="(error, index) in uploadTask.errors.slice(0, 10)"
                :key="index"
                class="px-0"
              >
                <template #prepend>
                  <v-icon color="error" size="small">mdi-alert-circle-outline</v-icon>
                </template>
                <v-list-item-title class="text-wrap">
                  {{ error.message || error }}
                </v-list-item-title>
                <v-list-item-subtitle v-if="error.line">
                  Строка: {{ error.line }}
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item v-if="uploadTask.errors.length > 10" class="px-0">
                <v-list-item-title class="text-center text-medium-emphasis">
                  ... и ещё {{ uploadTask.errors.length - 10 }} ошибок
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { groupsApi } from '@/services/api'
import { useAdaptivePolling } from '@/composables/useAdaptivePolling'
import GroupsUploadForm from '@/components/groups/GroupsUploadForm.vue'

const router = useRouter()

// Reactive data
const uploadTask = ref({
  taskId: null,
  status: '',
  progress: null,
  errors: [],
  message: ''
})
const refreshing = ref(false)
const redirectCountdown = ref(0)
const redirectInterval = ref(null)

// Адаптивный polling для загрузки групп
const polling = useAdaptivePolling(
  computed(() => String(uploadTask.value.taskId || '')),
  'general' // Для загрузки групп используем general конфигурацию
)

// Methods
const onUploadStarted = async (response) => {
  uploadTask.value = {
    taskId: response.taskId,
    status: 'pending',
    progress: null,
    errors: [],
    message: 'Файл загружен, начинается обработка...'
  }

  // Запускаем адаптивный polling
  await polling.startPolling(async () => {
    const statusResponse = await groupsApi.getTaskStatus(uploadTask.value.taskId)
    const data = statusResponse.data.data
    updateTaskStatus(data)
    return {
      status: data.status,
      progress: data.progress,
      errors: data.errors,
      ...data
    }
  })
}

const refreshStatus = async () => {
  if (!uploadTask.value.taskId) return

  refreshing.value = true
  try {
    const response = await groupsApi.getTaskStatus(uploadTask.value.taskId)
    console.log('Raw API response:', response.data)
    updateTaskStatus(response.data.data)
  } catch (error) {
    console.error('Error refreshing status:', error)
  } finally {
    refreshing.value = false
  }
}

const updateTaskStatus = (data) => {
  const previousStatus = uploadTask.value.status

  console.log('Updating task status:', {
    taskId: uploadTask.value.taskId,
    previousStatus,
    newStatus: data.status,
    data
  })

  uploadTask.value = {
    ...uploadTask.value,
    status: data.status || uploadTask.value.status,
    progress: data.progress || uploadTask.value.progress,
    errors: data.errors || uploadTask.value.errors,
    message: data.message || data.error || uploadTask.value.message
  }

  // Stop polling if task is complete
  if (['completed', 'failed'].includes(data.status)) {
    console.log('Task completed, stopping polling and starting redirect')
    polling.stopPolling()

    // Auto-redirect to groups page when task completes successfully
    if (data.status === 'completed' && previousStatus !== 'completed') {
      startRedirectCountdown()
    }
  }
}

// Старые методы polling удалены, используется useAdaptivePolling

const startRedirectCountdown = () => {
  redirectCountdown.value = 3 // Start with 3 seconds

  redirectInterval.value = setInterval(() => {
    redirectCountdown.value--

    if (redirectCountdown.value <= 0) {
      clearInterval(redirectInterval.value)
      redirectInterval.value = null
      router.push('/groups')
    }
  }, 1000)
}

// stopPolling удален, используется polling.stopPolling() из useAdaptivePolling

const stopRedirectCountdown = () => {
  if (redirectInterval.value) {
    clearInterval(redirectInterval.value)
    redirectInterval.value = null
  }
  redirectCountdown.value = 0
}

const downloadErrorReport = () => {
  if (!uploadTask.value.errors || uploadTask.value.errors.length === 0) return

  // Create error report content
  const reportContent = uploadTask.value.errors.map((error, index) => {
    if (typeof error === 'string') {
      return `${index + 1}. ${error}`
    }
    return `${index + 1}. Строка ${error.line || 'неизвестно'}: ${error.message || error}`
  }).join('\n')

  const content = `Отчёт об ошибках парсинга файла групп
Task ID: ${uploadTask.value.taskId}
Дата: ${new Date().toLocaleString('ru-RU')}
Всего ошибок: ${uploadTask.value.errors.length}

${reportContent}`

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `groups_upload_errors_${uploadTask.value.taskId}.txt`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
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
    'processing': 'Обрабатывается',
    'completed': 'Завершено',
    'failed': 'Ошибка'
  }
  return texts[status] || status
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

const getProgressPercentage = () => {
  if (!uploadTask.value.progress) return 0
  const { processed = 0, total = 0 } = uploadTask.value.progress
  if (total === 0) return 0
  return Math.round((processed / total) * 100)
}

const getMessageType = (status) => {
  const types = {
    'pending': 'info',
    'processing': 'info',
    'completed': 'success',
    'failed': 'error'
  }
  return types[status] || 'info'
}

// Lifecycle
onMounted(async () => {
  // Check if we have a task ID from route query
  if (router.currentRoute.value.query.taskId) {
    uploadTask.value.taskId = router.currentRoute.value.query.taskId
    await refreshStatus()

    // Запускаем адаптивный polling если задача еще выполняется
    if (['pending', 'processing'].includes(uploadTask.value.status)) {
      await polling.startPolling(async () => {
        const statusResponse = await groupsApi.getTaskStatus(uploadTask.value.taskId)
        const data = statusResponse.data.data
        updateTaskStatus(data)
        return {
          status: data.status,
          progress: data.progress,
          errors: data.errors,
          ...data
        }
      })
    }
  }
})

onUnmounted(() => {
  polling.stopPolling()
  stopRedirectCountdown()
})
</script>
