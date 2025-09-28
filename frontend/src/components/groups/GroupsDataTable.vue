<template>
  <div>
    <v-card elevation="2">
    <v-card-title class="d-flex align-center">
      <v-icon class="me-2" color="primary">mdi-table</v-icon>
      Список групп
      <v-spacer />
      <v-chip
        v-if="!isEmpty"
        color="primary"
        variant="tonal"
        size="small"
      >
        {{ pagination.total }} {{ getGroupsCountText(pagination.total) }}
      </v-chip>
    </v-card-title>

    <!-- Bulk Actions Toolbar -->
    <v-toolbar
      v-if="selectedGroups.length > 0"
      color="primary"
      variant="flat"
      density="compact"
      class="text-white"
    >
      <v-icon class="me-2">mdi-checkbox-marked-circle</v-icon>
      <span>Выбрано: {{ selectedGroups.length }}</span>
      <v-spacer />
      <v-btn
        variant="text"
        size="small"
        prepend-icon="mdi-delete"
        @click="handleBatchDelete"
        class="text-white"
      >
        Удалить выбранные
      </v-btn>
      <v-btn
        variant="text"
        size="small"
        icon="mdi-close"
        @click="clearSelection"
      />
    </v-toolbar>

    <!-- Loading -->
    <div v-if="loading" class="pa-8 text-center">
      <v-progress-circular
        indeterminate
        color="primary"
        size="48"
      />
      <p class="mt-4 text-body-2">Загрузка групп...</p>
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
          @click="refreshGroups"
        >
          Повторить
        </v-btn>
      </template>
    </v-alert>

    <!-- Empty State -->
    <div v-else-if="isEmpty" class="pa-8 text-center">
      <v-icon size="64" class="mb-4 text-medium-emphasis">
        mdi-account-group-outline
      </v-icon>
      <h3 class="text-h6 mb-2">Групп не найдено</h3>
      <p class="text-body-2 text-medium-emphasis mb-4">
        {{ hasFilters ? 'Попробуйте изменить фильтры поиска' : 'Загрузите файл с группами для начала работы' }}
      </p>
      <v-btn
        v-if="!hasFilters"
        color="primary"
        prepend-icon="mdi-upload"
        to="/groups/upload"
      >
        Загрузить группы
      </v-btn>
    </div>

    <!-- Data Table -->
    <v-data-table-server
      v-else
      v-model="selectedGroups"
      :headers="headers"
      :items="groups"
      :loading="loading"
      :items-length="pagination.total"
      :items-per-page="pagination.limit"
      :page="pagination.page"
      @update:page="handlePageChange"
      @update:items-per-page="handleItemsPerPageChange"
      item-value="id"
      show-select
      class="groups-table"
      no-data-text="Нет данных"
      loading-text="Загрузка..."
      items-per-page-text="Групп на странице:"
      :items-per-page-options="[10, 25, 50, 100]"
    >
      <!-- Group ID Column -->
      <template v-slot:[`item.id`]="{ item }">
        <v-chip
          size="small"
          variant="tonal"
          color="primary"
          class="font-mono"
        >
          {{ item.id }}
        </v-chip>
      </template>

      <!-- Name Column -->
      <template v-slot:[`item.name`]="{ item }">
        <div class="text-body-2 font-weight-medium">
          {{ item.name || 'Без названия' }}
        </div>
      </template>

      <!-- Status Column -->
      <template v-slot:[`item.status`]="{ item }">
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

      <!-- Upload Date Column -->
      <template v-slot:[`item.uploaded_at`]="{ item }">
        <div class="text-body-2">
          {{ formatDate(item.uploaded_at) }}
        </div>
      </template>

      <!-- Task ID Column -->
      <template v-slot:[`item.task_id`]="{ item }">
        <v-chip
          size="small"
          variant="outlined"
          color="info"
          class="font-mono"
        >
          {{ item.task_id.substring(0, 8) }}...
        </v-chip>
      </template>

      <!-- Actions Column -->
      <template v-slot:[`item.actions`]="{ item }">
        <div class="d-flex align-center gap-1">
          <v-tooltip text="Просмотреть детали">
            <template #activator="{ props }">
              <v-btn
                v-bind="props"
                icon="mdi-eye"
                size="small"
                variant="text"
                @click="viewDetails(item)"
              />
            </template>
          </v-tooltip>

          <v-tooltip text="Удалить группу">
            <template #activator="{ props }">
              <v-btn
                v-bind="props"
                icon="mdi-delete"
                size="small"
                variant="text"
                color="error"
                @click="handleSingleDelete(item)"
              />
            </template>
          </v-tooltip>
        </div>
      </template>
    </v-data-table-server>

    <!-- Pagination Info -->
    <v-card-actions v-if="pagination.total > 0" class="justify-center">
      <div class="text-caption text-medium-emphasis">
        Показано {{ getDisplayRangeText() }} из {{ pagination.total }} групп
      </div>
    </v-card-actions>
    </v-card>

    <!-- Single Delete Confirmation Dialog -->
    <v-dialog
      v-model="singleDeleteDialog.show"
      max-width="500px"
    >
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon class="me-2" color="error">mdi-alert-circle</v-icon>
          Подтверждение удаления
        </v-card-title>
        <v-card-text>
          <p class="mb-4">
            Вы действительно хотите удалить группу
            <strong>{{ singleDeleteDialog.group?.name || singleDeleteDialog.group?.id }}</strong>?
          </p>
          <p class="text-body-2 text-medium-emphasis">
            Это действие необратимо.
          </p>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="singleDeleteDialog.show = false"
            :disabled="singleDeleteDialog.loading"
          >
            Отмена
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            @click="confirmSingleDelete"
            :loading="singleDeleteDialog.loading"
          >
            Удалить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useGroupsStore } from '@/stores/groups'

const emit = defineEmits(['batch-delete'])

const groupsStore = useGroupsStore()
const {
  groups,
  loading,
  error,
  pagination,
  filters,
  isEmpty
} = storeToRefs(groupsStore)

// Reactive data
const selectedGroups = ref([])
const singleDeleteDialog = ref({
  show: false,
  group: null,
  loading: false
})

// Computed
const hasFilters = computed(() =>
  Object.values(filters.value).some(value =>
    value !== undefined && value !== '' && value !== null
  )
)

// Data
const headers = [
  { title: 'ID группы', key: 'id', width: '120px', sortable: false },
  { title: 'Название', key: 'name', sortable: false },
  { title: 'Статус', key: 'status', width: '120px', sortable: false },
  { title: 'Загружена', key: 'uploaded_at', width: '140px', sortable: false },
  { title: 'Задача', key: 'task_id', width: '140px', sortable: false },
  { title: 'Действия', key: 'actions', width: '120px', sortable: false }
]

// Methods
const refreshGroups = () => {
  groupsStore.fetchGroups()
}

const handlePageChange = (page) => {
  groupsStore.updateFilters({ page })
  groupsStore.fetchGroups()
}

const handleItemsPerPageChange = (itemsPerPage) => {
  groupsStore.updateFilters({ limit: itemsPerPage, page: 1 })
  groupsStore.fetchGroups()
}

const handleBatchDelete = () => {
  if (selectedGroups.value.length === 0) return
  emit('batch-delete', [...selectedGroups.value])
}

const handleSingleDelete = (group) => {
  singleDeleteDialog.value = {
    show: true,
    group,
    loading: false
  }
}

const confirmSingleDelete = async () => {
  if (!singleDeleteDialog.value.group) return

  singleDeleteDialog.value.loading = true

  try {
    await groupsStore.deleteGroup(singleDeleteDialog.value.group.id)
    singleDeleteDialog.value.show = false
  } catch (error) {
    console.error('Error deleting group:', error)
  } finally {
    singleDeleteDialog.value.loading = false
  }
}

const clearSelection = () => {
  selectedGroups.value = []
}

const viewDetails = (group) => {
  // TODO: Implement group details view
  console.log('View group details:', group)
}

// Helper functions
const getStatusColor = (status) => {
  const colors = {
    'valid': 'success',
    'invalid': 'error',
    'duplicate': 'warning',
    'pending': 'info'
  }
  return colors[status] || 'grey'
}

const getStatusIcon = (status) => {
  const icons = {
    'valid': 'mdi-check-circle',
    'invalid': 'mdi-alert-circle',
    'duplicate': 'mdi-content-duplicate',
    'pending': 'mdi-clock-outline'
  }
  return icons[status] || 'mdi-help'
}

const getStatusText = (status) => {
  const texts = {
    'valid': 'Валидная',
    'invalid': 'Невалидная',
    'duplicate': 'Дубликат',
    'pending': 'Ожидает'
  }
  return texts[status] || status
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

const getGroupsCountText = (count) => {
  const lastDigit = count % 10
  const lastTwoDigits = count % 100

  if (lastTwoDigits >= 11 && lastTwoDigits <= 14) {
    return 'групп'
  }

  if (lastDigit === 1) return 'группа'
  if (lastDigit >= 2 && lastDigit <= 4) return 'группы'
  return 'групп'
}

const getDisplayRangeText = () => {
  const { page = 1, limit = 20, total = 0 } = pagination.value
  const start = (page - 1) * limit + 1
  const end = Math.min(page * limit, total)
  return `${start}-${end}`
}
</script>

<style scoped>
.groups-table :deep(.v-data-table__tr) {
  cursor: default;
}

.font-mono {
  font-family: 'Roboto Mono', monospace;
}
</style>