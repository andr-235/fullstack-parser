<template>
  <v-card elevation="2">
    <v-card-title class="d-flex align-center">
      <v-icon class="me-2" color="primary">mdi-table</v-icon>
      Результаты
      <v-spacer />
      <v-btn
        variant="outlined"
        size="small"
        prepend-icon="mdi-download"
        @click="exportToCSV"
        :disabled="loading || results.length === 0"
      >
        Экспорт CSV
      </v-btn>
    </v-card-title>

    <!-- Filters -->
    <v-card-text>
      <v-row>
        <v-col cols="12" md="4">
          <v-text-field
            v-model="filters.groupId"
            label="ID группы"
            type="number"
            variant="outlined"
            density="compact"
            clearable
            @update:model-value="debouncedFetch"
          />
        </v-col>
        <v-col cols="12" md="4">
          <v-text-field
            v-model="filters.postId"
            label="ID поста"
            type="number"
            variant="outlined"
            density="compact"
            clearable
            @update:model-value="debouncedFetch"
          />
        </v-col>
        <v-col cols="12" md="4">
          <v-select
            v-model="filters.sentiment"
            :items="sentimentOptions"
            item-title="text"
            item-value="value"
            label="Настроение"
            variant="outlined"
            density="compact"
            clearable
            @update:model-value="fetchResults"
          />
        </v-col>
      </v-row>
    </v-card-text>

    <!-- Loading -->
    <div v-if="loading" class="pa-8 text-center">
      <v-progress-circular
        indeterminate
        color="primary"
        size="48"
      />
      <p class="mt-4 text-body-2">Загрузка результатов...</p>
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
          @click="fetchResults"
        >
          Повторить
        </v-btn>
      </template>
    </v-alert>

    <!-- Empty State -->
    <div v-else-if="results.length === 0" class="pa-8 text-center">
      <v-icon size="48" class="mb-4 text-medium-emphasis">
        mdi-database-search-outline
      </v-icon>
      <h4 class="text-h6 mb-2">Нет результатов</h4>
      <p class="text-body-2 text-medium-emphasis">
        {{ hasFilters ? 'Попробуйте изменить фильтры поиска' : 'Результаты не найдены' }}
      </p>
    </div>

    <!-- Results Table -->
    <v-data-table-server
      v-else
      :headers="headers"
      :items="results"
      :loading="loading"
      :items-length="pagination.total"
      :items-per-page="pagination.limit"
      :page="pagination.page"
      @update:page="handlePageChange"
      class="results-table"
      no-data-text="Нет данных"
      loading-text="Загрузка..."
      items-per-page-text="Результатов на странице:"
      :items-per-page-options="[10, 25, 50, 100]"
      @update:items-per-page="handleItemsPerPageChange"
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

      <!-- Group ID Column -->
      <template #item.groupId="{ item }">
        <span class="font-weight-medium">{{ item.groupId || '-' }}</span>
      </template>

      <!-- Post ID Column -->
      <template #item.postId="{ item }">
        <span class="font-weight-medium">{{ item.postId || '-' }}</span>
      </template>

      <!-- Content Column -->
      <template #item.content="{ item }">
        <div class="content-cell">
          <p class="text-body-2 text-truncate mb-1" style="max-width: 300px">
            {{ item.content || item.text || '-' }}
          </p>
          <v-btn
            v-if="(item.content || item.text) && (item.content || item.text).length > 100"
            variant="text"
            size="x-small"
            @click="showContentDialog(item)"
          >
            Показать полностью
          </v-btn>
        </div>
      </template>

      <!-- Sentiment Column -->
      <template #item.sentiment="{ item }">
        <v-chip
          v-if="item.sentiment"
          size="small"
          :color="getSentimentColor(item.sentiment)"
          variant="flat"
        >
          {{ getSentimentText(item.sentiment) }}
        </v-chip>
        <span v-else class="text-medium-emphasis">-</span>
      </template>

      <!-- Author Column -->
      <template #item.author="{ item }">
        <div class="d-flex align-center">
          <v-avatar v-if="item.author?.avatar" size="24" class="me-2">
            <v-img :src="item.author.avatar" />
          </v-avatar>
          <div>
            <div class="text-body-2 font-weight-medium">
              {{ item.author?.name || item.authorName || '-' }}
            </div>
            <div v-if="item.author?.id || item.authorId" class="text-caption text-medium-emphasis">
              ID: {{ item.author?.id || item.authorId }}
            </div>
          </div>
        </div>
      </template>

      <!-- Date Column -->
      <template #item.date="{ item }">
        <div class="text-body-2">
          {{ formatDate(item.date || item.createdAt) }}
        </div>
      </template>
    </v-data-table-server>

    <!-- Pagination Info -->
    <v-card-actions v-if="pagination.total > 0" class="justify-center">
      <div class="text-caption text-medium-emphasis">
        Показано {{ ((pagination.page - 1) * pagination.limit) + 1 }}-{{ Math.min(pagination.page * pagination.limit, pagination.total) }}
        из {{ pagination.total }} результатов
      </div>
    </v-card-actions>
  </v-card>

  <!-- Content Dialog -->
  <v-dialog
    v-model="contentDialog.show"
    max-width="600px"
  >
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="me-2">mdi-text</v-icon>
        Полный текст
      </v-card-title>
      <v-card-text>
        <p class="text-body-1">
          {{ contentDialog.content }}
        </p>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn
          variant="text"
          @click="contentDialog.show = false"
        >
          Закрыть
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getResults } from '@/services/api'

// Simple debounce implementation
const debounce = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

const props = defineProps({
  taskId: {
    type: [String, Number],
    required: true
  }
})

// Reactive data
const results = ref([])
const loading = ref(false)
const error = ref('')
const pagination = ref({
  page: 1,
  limit: 25,
  total: 0
})
const filters = ref({
  groupId: '',
  postId: '',
  sentiment: ''
})
const contentDialog = ref({
  show: false,
  content: ''
})

// Computed
const hasFilters = computed(() =>
  filters.value.groupId || filters.value.postId || filters.value.sentiment
)

// Data
const sentimentOptions = [
  { text: 'Все', value: '' },
  { text: 'Положительное', value: 'positive' },
  { text: 'Нейтральное', value: 'neutral' },
  { text: 'Отрицательное', value: 'negative' }
]

const headers = [
  { title: 'ID', key: 'id', width: '80px', sortable: false },
  { title: 'Группа', key: 'groupId', width: '100px', sortable: false },
  { title: 'Пост', key: 'postId', width: '100px', sortable: false },
  { title: 'Содержимое', key: 'content', sortable: false },
  { title: 'Настроение', key: 'sentiment', width: '120px', sortable: false },
  { title: 'Автор', key: 'author', width: '180px', sortable: false },
  { title: 'Дата', key: 'date', width: '140px', sortable: false }
]

// Methods
const fetchResults = async () => {
  loading.value = true
  error.value = ''

  try {
    const params = {
      limit: pagination.value.limit,
      offset: (pagination.value.page - 1) * pagination.value.limit,
      ...(filters.value.groupId && { groupId: parseInt(filters.value.groupId) }),
      ...(filters.value.postId && { postId: parseInt(filters.value.postId) }),
      ...(filters.value.sentiment && { sentiment: filters.value.sentiment })
    }

    const response = await getResults(props.taskId, params)
    const data = response.data

    results.value = data.results || []
    pagination.value.total = data.total || 0
  } catch (err) {
    error.value = err.response?.data?.message || err.message || 'Ошибка загрузки результатов'
    console.error('Error fetching results:', err)
  } finally {
    loading.value = false
  }
}

const debouncedFetch = debounce(fetchResults, 500)

const handlePageChange = (page) => {
  pagination.value.page = page
  fetchResults()
}

const handleItemsPerPageChange = (itemsPerPage) => {
  pagination.value.limit = itemsPerPage
  pagination.value.page = 1
  fetchResults()
}

const showContentDialog = (item) => {
  contentDialog.value = {
    show: true,
    content: item.content || item.text || ''
  }
}

const exportToCSV = () => {
  if (results.value.length === 0) return

  // Prepare CSV headers
  const csvHeaders = ['ID', 'Group ID', 'Post ID', 'Content', 'Sentiment', 'Author', 'Date']

  // Prepare CSV rows
  const csvRows = results.value.map(item => [
    item.id || '',
    item.groupId || '',
    item.postId || '',
    `"${(item.content || item.text || '').replace(/"/g, '""')}"`,
    item.sentiment || '',
    item.author?.name || item.authorName || '',
    item.date || item.createdAt || ''
  ])

  // Create CSV content
  const csvContent = [csvHeaders, ...csvRows]
    .map(row => row.join(','))
    .join('\n')

  // Download CSV
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `task_${props.taskId}_results.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Helper functions
const getSentimentColor = (sentiment) => {
  const colors = {
    'positive': 'green',
    'neutral': 'grey',
    'negative': 'red'
  }
  return colors[sentiment] || 'grey'
}

const getSentimentText = (sentiment) => {
  const texts = {
    'positive': 'Позитивное',
    'neutral': 'Нейтральное',
    'negative': 'Негативное'
  }
  return texts[sentiment] || sentiment
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

// Watchers
watch(() => props.taskId, () => {
  // Reset filters and pagination when task changes
  filters.value = {
    groupId: '',
    postId: '',
    sentiment: ''
  }
  pagination.value.page = 1
  fetchResults()
})

// Lifecycle
onMounted(() => {
  fetchResults()
})
</script>

<style scoped>
.results-table :deep(.v-data-table__tr) {
  cursor: default;
}

.content-cell {
  min-width: 200px;
  max-width: 300px;
}

.text-truncate {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
</style>