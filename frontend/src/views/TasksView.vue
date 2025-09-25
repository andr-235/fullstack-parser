<template>
  <v-container fluid class="pa-6">
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold">Задачи</h1>
        <p class="text-body-1 text-medium-emphasis mt-1">
          Управление задачами сбора данных
        </p>
      </div>

      <div class="d-flex gap-2">
        <v-btn
          color="primary"
          variant="outlined"
          prepend-icon="mdi-plus"
          @click="showCreateCommentsModal = true"
        >
          Задача комментариев
        </v-btn>
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          @click="showCreateVkCollectModal = true"
        >
          VK Collect задача
        </v-btn>
      </div>
    </div>

    <!-- Filters -->
    <v-card class="mb-6" flat>
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedStatus"
              :items="statusOptions"
              item-title="text"
              item-value="value"
              label="Фильтр по статусу"
              clearable
              variant="outlined"
              density="compact"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-btn
              variant="outlined"
              prepend-icon="mdi-refresh"
              @click="refreshTasks"
              :loading="loading"
            >
              Обновить
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Tasks Table -->
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="me-2">mdi-format-list-bulleted</v-icon>
        Список задач
        <v-spacer />
        <v-chip
          v-if="!isEmpty"
          color="primary"
          variant="tonal"
          size="small"
        >
          {{ pagination.total }} {{ getTasksCountText(pagination.total) }}
        </v-chip>
      </v-card-title>

      <!-- Loading -->
      <div v-if="loading" class="pa-8 text-center">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        />
        <p class="mt-4 text-body-1">Загрузка задач...</p>
      </div>

      <!-- Error -->
      <v-alert
        v-else-if="error"
        type="error"
        class="ma-4"
        :text="error"
        variant="tonal"
      >
        <template #append>
          <v-btn
            variant="text"
            size="small"
            @click="refreshTasks"
          >
            Повторить
          </v-btn>
        </template>
      </v-alert>

      <!-- Empty State -->
      <div v-else-if="isEmpty" class="pa-8 text-center">
        <v-icon size="64" class="mb-4 text-medium-emphasis">
          mdi-clipboard-list-outline
        </v-icon>
        <h3 class="text-h6 mb-2">Задач не найдено</h3>
        <p class="text-body-2 text-medium-emphasis mb-4">
          {{ selectedStatus ? 'Нет задач с выбранным статусом' : 'Создайте первую задачу для сбора данных' }}
        </p>
        <v-btn
          v-if="!selectedStatus"
          color="primary"
          prepend-icon="mdi-plus"
          @click="showCreateVkCollectModal = true"
        >
          Создать задачу
        </v-btn>
      </div>

      <!-- Tasks Data Table -->
      <v-data-table-server
        v-else
        :headers="headers"
        :items="tasks"
        :loading="loading"
        :items-length="pagination.total"
        :items-per-page="pagination.limit"
        :page="pagination.page"
        @update:page="handlePageChange"
        @click:row="handleRowClick"
        hover
        class="tasks-table"
        no-data-text="Нет данных"
        loading-text="Загрузка..."
        items-per-page-text="Задач на странице:"
      >
        <!-- ID Column -->
        <template #item.id="{ item }">
          <v-chip
            size="small"
            variant="tonal"
            color="primary"
          >
            {{ item.id }}
          </v-chip>
        </template>

        <!-- Type Column -->
        <template #item.type="{ item }">
          <v-chip
            size="small"
            :color="getTypeColor(item.type)"
            variant="flat"
          >
            <v-icon start size="small">
              {{ getTypeIcon(item.type) }}
            </v-icon>
            {{ getTypeText(item.type) }}
          </v-chip>
        </template>

        <!-- Status Column -->
        <template #item.status="{ item }">
          <v-chip
            size="small"
            :color="getStatusColor(item.status)"
            variant="flat"
          >
            <v-icon start size="small">
              {{ getStatusIcon(item.status) }}
            </v-icon>
            {{ getStatusText(item.status) }}
          </v-chip>
        </template>

        <!-- Progress Column -->
        <template #item.progress="{ item }">
          <div class="d-flex align-center" style="min-width: 120px">
            <v-progress-linear
              :model-value="getProgressValue(item)"
              :color="getProgressColor(item.status)"
              height="6"
              rounded
              class="me-2"
            />
            <span class="text-caption">{{ getProgressText(item) }}</span>
          </div>
        </template>

        <!-- Created At Column -->
        <template #item.createdAt="{ item }">
          <div class="text-body-2">
            {{ formatDate(item.createdAt) }}
          </div>
        </template>

        <!-- Actions Column -->
        <template #item.actions="{ item }">
          <div class="d-flex align-center gap-1">
            <v-tooltip text="Перейти к деталям">
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon="mdi-eye"
                  size="small"
                  variant="text"
                  @click.stop="goToTaskDetails(item.id)"
                />
              </template>
            </v-tooltip>

            <v-tooltip v-if="item.status === 'pending'" text="Запустить задачу">
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon="mdi-play"
                  size="small"
                  variant="text"
                  color="success"
                  @click.stop="startTask(item.id)"
                />
              </template>
            </v-tooltip>
          </div>
        </template>
      </v-data-table-server>
    </v-card>

    <!-- Create Comments Task Modal -->
    <CreateCommentsTaskModal
      v-model="showCreateCommentsModal"
      @created="onTaskCreated"
    />

    <!-- Create VK Collect Task Modal -->
    <CreateVkCollectTaskModal
      v-model="showCreateVkCollectModal"
      @created="onTaskCreated"
    />

    <!-- Success Snackbar -->
    <v-snackbar
      v-model="showSuccessMessage"
      color="success"
      timeout="5000"
      location="top"
    >
      {{ successMessage }}
      <template #actions>
        <v-btn
          v-if="createdTaskId"
          variant="text"
          size="small"
          @click="goToTaskDetails(createdTaskId)"
        >
          Перейти к деталям
        </v-btn>
        <v-btn
          variant="text"
          @click="showSuccessMessage = false"
        >
          Закрыть
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useTasksStore } from '@/stores/tasks'
import CreateCommentsTaskModal from '@/components/tasks/CreateCommentsTaskModal.vue'
import CreateVkCollectTaskModal from '@/components/tasks/CreateVkCollectTaskModal.vue'

const router = useRouter()
const tasksStore = useTasksStore()

const {
  tasks,
  loading,
  error,
  pagination,
  filters,
  isEmpty
} = storeToRefs(tasksStore)

// Local state
const showCreateCommentsModal = ref(false)
const showCreateVkCollectModal = ref(false)
const showSuccessMessage = ref(false)
const successMessage = ref('')
const createdTaskId = ref(null)

// Computed
const selectedStatus = computed({
  get: () => filters.value.status,
  set: (value) => {
    tasksStore.setStatusFilter(value || '')
  }
})

// Data
const statusOptions = [
  { text: 'Все статусы', value: '' },
  { text: 'Ожидает', value: 'pending' },
  { text: 'В процессе', value: 'processing' },
  { text: 'Завершена', value: 'completed' },
  { text: 'Ошибка', value: 'failed' }
]

const headers = [
  { title: 'ID', key: 'id', width: '80px', sortable: false },
  { title: 'Тип', key: 'type', width: '140px', sortable: false },
  { title: 'Статус', key: 'status', width: '130px', sortable: false },
  { title: 'Прогресс', key: 'progress', width: '160px', sortable: false },
  { title: 'Создана', key: 'createdAt', width: '140px', sortable: false },
  { title: 'Действия', key: 'actions', width: '120px', sortable: false }
]

// Methods
const refreshTasks = async () => {
  await tasksStore.fetchTasks()
}

const handlePageChange = (page) => {
  tasksStore.setPage(page)
  tasksStore.fetchTasks()
}

const handleRowClick = (event, { item }) => {
  goToTaskDetails(item.id)
}

const goToTaskDetails = (taskId) => {
  router.push(`/tasks/${taskId}`)
}

const startTask = async (taskId) => {
  // TODO: Implement start task functionality
  console.log('Starting task:', taskId)
}

const onTaskCreated = (response) => {
  createdTaskId.value = response.taskId
  successMessage.value = `Задача #${response.taskId} создана успешно`
  showSuccessMessage.value = true
  showCreateCommentsModal.value = false
  showCreateVkCollectModal.value = false
}

// Helper functions
const getTypeColor = (type) => {
  const colors = {
    'comments': 'blue',
    'vk_collect': 'green',
    'groups': 'purple'
  }
  return colors[type] || 'grey'
}

const getTypeIcon = (type) => {
  const icons = {
    'comments': 'mdi-comment-multiple',
    'vk_collect': 'mdi-download',
    'groups': 'mdi-account-group'
  }
  return icons[type] || 'mdi-help'
}

const getTypeText = (type) => {
  const texts = {
    'comments': 'Комментарии',
    'vk_collect': 'VK Сбор',
    'groups': 'Группы'
  }
  return texts[type] || type
}

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

const getProgressValue = (item) => {
  if (!item.progress) return 0
  if (item.status === 'completed') return 100
  if (item.status === 'failed') return 0

  const { processed = 0, total = 0 } = item.progress
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

const getProgressText = (item) => {
  if (!item.progress) return '0%'
  if (item.status === 'completed') return '100%'
  if (item.status === 'failed') return 'Ошибка'

  const { processed = 0, total = 0 } = item.progress
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

const getTasksCountText = (count) => {
  const lastDigit = count % 10
  const lastTwoDigits = count % 100

  if (lastTwoDigits >= 11 && lastTwoDigits <= 14) {
    return 'задач'
  }

  if (lastDigit === 1) return 'задача'
  if (lastDigit >= 2 && lastDigit <= 4) return 'задачи'
  return 'задач'
}

// Watch for status changes
watch(selectedStatus, () => {
  tasksStore.fetchTasks()
})

// Load tasks on mount
onMounted(() => {
  tasksStore.fetchTasks()
})
</script>

<style scoped>
.tasks-table :deep(.v-data-table__tr) {
  cursor: pointer;
}

.tasks-table :deep(.v-data-table__tr:hover) {
  background-color: rgba(var(--v-theme-primary), 0.04) !important;
}
</style>