<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div class="d-flex align-center">
        <v-btn
          icon="mdi-arrow-left"
          variant="text"
          size="small"
          class="mr-2"
          @click="$router.push('/groups')"
        />
        <div>
          <h1 class="text-h4 font-weight-bold">Статистика групп</h1>
          <p class="text-body-1 text-medium-emphasis mt-1">
            Task #{{ taskId }} • Анализ загруженных групп
          </p>
        </div>
      </div>

      <div class="d-flex gap-2">
        <v-btn
          variant="outlined"
          prepend-icon="mdi-refresh"
          @click="loadStats"
          :loading="loading"
        >
          Обновить
        </v-btn>
        <v-btn
          variant="outlined"
          prepend-icon="mdi-download"
          @click="exportReport"
          :disabled="!stats"
        >
          Экспорт отчёта
        </v-btn>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !stats" class="d-flex justify-center align-center" style="height: 400px">
      <v-progress-circular
        indeterminate
        color="primary"
        size="64"
      />
      <div class="ml-4">
        <h3 class="text-h6">Загрузка статистики...</h3>
        <p class="text-body-2 text-medium-emphasis">Анализ данных групп</p>
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
        Ошибка загрузки статистики
      </template>
      {{ error }}
      <template #append>
        <v-btn
          variant="text"
          size="small"
          @click="loadStats"
        >
          Повторить
        </v-btn>
      </template>
    </v-alert>

    <!-- Stats Not Found -->
    <div v-else-if="!stats" class="text-center pa-8">
      <v-icon size="64" class="mb-4 text-medium-emphasis">
        mdi-chart-line-variant
      </v-icon>
      <h3 class="text-h6 mb-2">Статистика недоступна</h3>
      <p class="text-body-2 text-medium-emphasis mb-4">
        Статистика для Task #{{ taskId }} не найдена или еще не готова
      </p>
      <v-btn
        color="primary"
        to="/groups"
        prepend-icon="mdi-arrow-left"
      >
        Вернуться к группам
      </v-btn>
    </div>

    <!-- Statistics Content -->
    <div v-else>
      <!-- KPI Cards -->
      <v-row class="mb-6">
        <v-col cols="12" sm="6" md="3">
          <v-card color="success" variant="tonal" class="text-center pa-4">
            <v-icon size="48" class="mb-2">mdi-check-circle</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.valid || 0 }}</div>
            <div class="text-body-1">Валидные группы</div>
            <div v-if="stats.total" class="text-caption text-medium-emphasis">
              {{ getPercentage(stats.valid, stats.total) }}%
            </div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card color="error" variant="tonal" class="text-center pa-4">
            <v-icon size="48" class="mb-2">mdi-alert-circle</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.invalid || 0 }}</div>
            <div class="text-body-1">Невалидные</div>
            <div v-if="stats.total" class="text-caption text-medium-emphasis">
              {{ getPercentage(stats.invalid, stats.total) }}%
            </div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card color="warning" variant="tonal" class="text-center pa-4">
            <v-icon size="48" class="mb-2">mdi-content-duplicate</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.duplicates || 0 }}</div>
            <div class="text-body-1">Дубликаты</div>
            <div v-if="stats.total" class="text-caption text-medium-emphasis">
              {{ getPercentage(stats.duplicates, stats.total) }}%
            </div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card color="primary" variant="tonal" class="text-center pa-4">
            <v-icon size="48" class="mb-2">mdi-account-group</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.total || 0 }}</div>
            <div class="text-body-1">Всего групп</div>
            <div class="text-caption text-medium-emphasis">
              Обработано
            </div>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <!-- Pie Chart -->
        <v-col cols="12" md="6">
          <v-card elevation="2" class="pa-4">
            <v-card-title class="d-flex align-center pb-4">
              <v-icon class="me-2" color="primary">mdi-chart-pie</v-icon>
              Распределение по статусам
            </v-card-title>
            <div class="d-flex justify-center">
              <canvas
                ref="pieChartCanvas"
                width="300"
                height="300"
              />
            </div>
          </v-card>
        </v-col>

        <!-- Column Chart -->
        <v-col cols="12" md="6">
          <v-card elevation="2" class="pa-4">
            <v-card-title class="d-flex align-center pb-4">
              <v-icon class="me-2" color="primary">mdi-chart-bar</v-icon>
              Статистика по категориям
            </v-card-title>
            <div class="d-flex justify-center">
              <canvas
                ref="columnChartCanvas"
                width="300"
                height="300"
              />
            </div>
          </v-card>
        </v-col>
      </v-row>

      <!-- Problematic Groups Table -->
      <v-card v-if="stats.problematicGroups && stats.problematicGroups.length > 0" class="mt-6" elevation="2">
        <v-card-title class="d-flex align-center">
          <v-icon class="me-2" color="error">mdi-alert-circle</v-icon>
          Проблемные группы
          <v-spacer />
          <v-chip color="error" variant="tonal" size="small">
            {{ stats.problematicGroups.length }}
          </v-chip>
        </v-card-title>

        <v-data-table
          :headers="problematicGroupsHeaders"
          :items="stats.problematicGroups"
          :items-per-page="10"
          class="problematic-groups-table"
          no-data-text="Проблемных групп не найдено"
          items-per-page-text="Групп на странице:"
        >
          <!-- Group ID Column -->
          <template #item.groupId="{ item }">
            <v-chip
              size="small"
              variant="tonal"
              color="error"
              class="font-mono"
            >
              {{ item.groupId }}
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

          <!-- Reason Column -->
          <template #item.reason="{ item }">
            <div class="text-body-2 text-wrap" style="max-width: 300px">
              {{ item.reason || item.error || 'Неизвестная ошибка' }}
            </div>
          </template>

          <!-- Actions Column -->
          <template #item.actions="{ item }">
            <v-tooltip text="Перейти к деталям задачи">
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon="mdi-open-in-new"
                  size="small"
                  variant="text"
                  :to="`/tasks/${taskId}`"
                />
              </template>
            </v-tooltip>
          </template>
        </v-data-table>
      </v-card>

      <!-- Additional Statistics -->
      <v-card class="mt-6" elevation="2">
        <v-card-title class="d-flex align-center">
          <v-icon class="me-2" color="primary">mdi-information</v-icon>
          Дополнительная информация
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <div class="mb-4">
                <div class="text-caption text-medium-emphasis">Время обработки</div>
                <div class="text-body-1 font-weight-medium">
                  {{ formatDuration(stats.processingTime) }}
                </div>
              </div>
              <div class="mb-4">
                <div class="text-caption text-medium-emphasis">Файл источник</div>
                <div class="text-body-1 font-weight-medium">
                  {{ stats.sourceFile || 'Не указан' }}
                </div>
              </div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="mb-4">
                <div class="text-caption text-medium-emphasis">Дата обработки</div>
                <div class="text-body-1 font-weight-medium">
                  {{ formatDate(stats.processedAt) }}
                </div>
              </div>
              <div class="mb-4">
                <div class="text-caption text-medium-emphasis">Успешность</div>
                <div class="text-body-1 font-weight-medium">
                  {{ getSuccessRate() }}%
                </div>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </div>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { groupsApi } from '@/services/api'

const route = useRoute()
const router = useRouter()

// Reactive data
const stats = ref(null)
const loading = ref(false)
const error = ref('')
const pieChartCanvas = ref(null)
const columnChartCanvas = ref(null)

// Computed
const taskId = computed(() => route.params.taskId)

// Data
const problematicGroupsHeaders = [
  { title: 'ID группы', key: 'groupId', width: '120px', sortable: false },
  { title: 'Статус', key: 'status', width: '120px', sortable: false },
  { title: 'Причина проблемы', key: 'reason', sortable: false },
  { title: 'Действия', key: 'actions', width: '100px', sortable: false }
]

// Methods
const loadStats = async () => {
  loading.value = true
  error.value = ''

  try {
    // TODO: Replace with actual API call when backend is ready
    // const response = await groupsApi.getGroupsStats(taskId.value)
    // stats.value = response.data

    // Mock data for demonstration
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API delay
    stats.value = {
      total: 1250,
      valid: 980,
      invalid: 180,
      duplicates: 90,
      processingTime: 45000, // milliseconds
      processedAt: new Date().toISOString(),
      sourceFile: 'vk_groups_list.txt',
      problematicGroups: [
        {
          groupId: '12345',
          status: 'invalid',
          reason: 'Группа не существует или заблокирована'
        },
        {
          groupId: '67890',
          status: 'invalid',
          reason: 'Нет доступа к группе'
        },
        {
          groupId: '11111',
          status: 'duplicate',
          reason: 'Дубликат группы 22222'
        }
      ]
    }

    // Draw charts after data is loaded
    await nextTick()
    drawCharts()
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = 'Статистика для данной задачи не найдена'
    } else {
      error.value = err.response?.data?.message || err.message || 'Ошибка загрузки статистики'
    }
    console.error('Error loading stats:', err)
  } finally {
    loading.value = false
  }
}

const drawCharts = () => {
  if (!stats.value) return

  drawPieChart()
  drawColumnChart()
}

const drawPieChart = () => {
  const canvas = pieChartCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  const centerX = canvas.width / 2
  const centerY = canvas.height / 2
  const radius = Math.min(centerX, centerY) - 20

  const data = [
    { label: 'Валидные', value: stats.value.valid, color: '#4CAF50' },
    { label: 'Невалидные', value: stats.value.invalid, color: '#F44336' },
    { label: 'Дубликаты', value: stats.value.duplicates, color: '#FF9800' }
  ]

  let currentAngle = 0
  const total = stats.value.total

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // Draw pie segments
  data.forEach(segment => {
    const sliceAngle = (segment.value / total) * 2 * Math.PI

    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle)
    ctx.lineTo(centerX, centerY)
    ctx.fillStyle = segment.color
    ctx.fill()

    // Draw label
    const labelAngle = currentAngle + sliceAngle / 2
    const labelX = centerX + Math.cos(labelAngle) * (radius * 0.7)
    const labelY = centerY + Math.sin(labelAngle) * (radius * 0.7)

    ctx.fillStyle = '#FFFFFF'
    ctx.font = '14px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(segment.value.toString(), labelX, labelY)

    currentAngle += sliceAngle
  })
}

const drawColumnChart = () => {
  const canvas = columnChartCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  const margin = 40
  const chartWidth = canvas.width - 2 * margin
  const chartHeight = canvas.height - 2 * margin

  const data = [
    { label: 'Валидные', value: stats.value.valid, color: '#4CAF50' },
    { label: 'Невалидные', value: stats.value.invalid, color: '#F44336' },
    { label: 'Дубликаты', value: stats.value.duplicates, color: '#FF9800' }
  ]

  const maxValue = Math.max(...data.map(d => d.value))
  const barWidth = chartWidth / data.length * 0.8
  const barSpacing = chartWidth / data.length * 0.2

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // Draw bars
  data.forEach((item, index) => {
    const barHeight = (item.value / maxValue) * chartHeight
    const x = margin + index * (barWidth + barSpacing) + barSpacing / 2
    const y = margin + chartHeight - barHeight

    ctx.fillStyle = item.color
    ctx.fillRect(x, y, barWidth, barHeight)

    // Draw value label
    ctx.fillStyle = '#000000'
    ctx.font = '12px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(item.value.toString(), x + barWidth / 2, y - 5)

    // Draw category label
    ctx.fillText(item.label, x + barWidth / 2, margin + chartHeight + 20)
  })
}

const exportReport = () => {
  if (!stats.value) return

  const reportData = {
    taskId: taskId.value,
    generatedAt: new Date().toISOString(),
    statistics: stats.value
  }

  const dataStr = JSON.stringify(reportData, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json;charset=utf-8' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `groups_stats_${taskId.value}.json`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Helper functions
const getPercentage = (value, total) => {
  if (!total) return 0
  return Math.round((value / total) * 100)
}

const getSuccessRate = () => {
  if (!stats.value || !stats.value.total) return 0
  return getPercentage(stats.value.valid, stats.value.total)
}

const getStatusColor = (status) => {
  const colors = {
    'valid': 'success',
    'invalid': 'error',
    'duplicate': 'warning'
  }
  return colors[status] || 'grey'
}

const getStatusIcon = (status) => {
  const icons = {
    'valid': 'mdi-check-circle',
    'invalid': 'mdi-alert-circle',
    'duplicate': 'mdi-content-duplicate'
  }
  return icons[status] || 'mdi-help'
}

const getStatusText = (status) => {
  const texts = {
    'valid': 'Валидная',
    'invalid': 'Невалидная',
    'duplicate': 'Дубликат'
  }
  return texts[status] || status
}

const formatDuration = (ms) => {
  if (!ms) return 'Неизвестно'

  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)

  if (hours > 0) {
    return `${hours}ч ${minutes % 60}м ${seconds % 60}с`
  } else if (minutes > 0) {
    return `${minutes}м ${seconds % 60}с`
  } else {
    return `${seconds}с`
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Неизвестно'

  const date = new Date(dateString)
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(date)
}

// Lifecycle
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.font-mono {
  font-family: 'Roboto Mono', monospace;
}

.problematic-groups-table :deep(.v-data-table__tr) {
  cursor: default;
}

canvas {
  max-width: 100%;
  height: auto;
}
</style>