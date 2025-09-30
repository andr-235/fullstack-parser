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
      <v-btn
        v-if="!isEmpty"
        color="error"
        variant="text"
        prepend-icon="mdi-delete-sweep"
        @click="handleClearAll"
        class="ms-2"
      >
        Очистить таблицу
      </v-btn>
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

      <!-- VK ID Column -->
      <template v-slot:[`item.vk_id`]="{ item }">
        <a
          :href="item.screenName ? `https://vk.com/${item.screenName}` : `https://vk.com/club${item.vkId}`"
          target="_blank"
          class="text-decoration-none"
        >
          <v-chip
            size="small"
            variant="outlined"
            color="primary"
            class="font-mono"
          >
            {{ item.vkId }}
            <v-icon end size="x-small">mdi-open-in-new</v-icon>
          </v-chip>
        </a>
      </template>

      <!-- Name Column -->
      <template v-slot:[`item.name`]="{ item }">
        <div class="d-flex align-center">
          <v-avatar v-if="item.photo_50" size="32" class="me-2">
            <v-img :src="item.photo_50" :alt="item.name" />
          </v-avatar>
          <div>
            <div class="text-body-2 font-weight-medium">
              {{ item.name || 'Без названия' }}
            </div>
            <div v-if="item.description" class="text-caption text-medium-emphasis text-truncate" style="max-width: 300px;">
              {{ item.description }}
            </div>
          </div>
        </div>
      </template>

      <!-- Screen Name Column -->
      <template v-slot:[`item.screen_name`]="{ item }">
        <a
          v-if="item.screen_name"
          :href="`https://vk.com/${item.screen_name}`"
          target="_blank"
          class="text-decoration-none"
        >
          <v-chip
            size="small"
            variant="text"
            color="info"
          >
            {{ item.screen_name }}
            <v-icon end size="x-small">mdi-open-in-new</v-icon>
          </v-chip>
        </a>
        <span v-else class="text-medium-emphasis">-</span>
      </template>

      <!-- Members Count Column -->
      <template v-slot:[`item.members_count`]="{ item }">
        <div v-if="item.members_count !== null && item.members_count !== undefined" class="text-body-2">
          <v-icon size="small" class="me-1">mdi-account-group</v-icon>
          {{ formatNumber(item.members_count) }}
        </div>
        <span v-else class="text-medium-emphasis">-</span>
      </template>

      <!-- Is Closed Column -->
      <template v-slot:[`item.is_closed`]="{ item }">
        <v-chip
          size="small"
          :color="getClosedColor(item.is_closed)"
          variant="tonal"
        >
          <v-icon start size="small">
            {{ getClosedIcon(item.is_closed) }}
          </v-icon>
          {{ getClosedText(item.is_closed) }}
        </v-chip>
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
      <template v-slot:[`item.uploadedAt`]="{ item }">
        <div class="text-body-2">
          {{ formatDate(item.uploadedAt) }}
        </div>
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

    <!-- Clear All Confirmation Dialog -->
    <v-dialog
      v-model="clearAllDialog.show"
      max-width="500px"
    >
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon class="me-2" color="error">mdi-alert-circle</v-icon>
          Подтверждение очистки
        </v-card-title>
        <v-card-text>
          <p class="mb-4">
            Вы действительно хотите удалить <strong>все группы</strong> из базы данных?
          </p>
          <p class="text-body-2 text-medium-emphasis mb-2">
            Это действие необратимо. Будет удалено <strong>{{ pagination.total }}</strong> {{ getGroupsCountText(pagination.total) }}.
          </p>
          <v-alert
            type="warning"
            variant="tonal"
            density="compact"
            class="mt-4"
          >
            <div class="text-body-2">
              Внимание: все данные будут безвозвратно утеряны!
            </div>
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="clearAllDialog.show = false"
            :disabled="clearAllDialog.loading"
          >
            Отмена
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            @click="confirmClearAll"
            :loading="clearAllDialog.loading"
          >
            Удалить все
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
const clearAllDialog = ref({
  show: false,
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
  { title: 'VK ID', key: 'vk_id', width: '120px', sortable: false },
  { title: 'Название', key: 'name', sortable: false },
  { title: 'Короткое имя', key: 'screen_name', width: '140px', sortable: false },
  { title: 'Участники', key: 'members_count', width: '120px', sortable: false },
  { title: 'Тип', key: 'is_closed', width: '100px', sortable: false },
  { title: 'Статус', key: 'status', width: '120px', sortable: false },
  { title: 'Загружена', key: 'uploadedAt', width: '140px', sortable: false },
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

const handleClearAll = () => {
  clearAllDialog.value.show = true
}

const confirmClearAll = async () => {
  clearAllDialog.value.loading = true

  try {
    await groupsStore.deleteAllGroups()
    clearAllDialog.value.show = false
    selectedGroups.value = []
  } catch (error) {
    console.error('Error clearing all groups:', error)
  } finally {
    clearAllDialog.value.loading = false
  }
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

const formatNumber = (num) => {
  if (num === null || num === undefined) return '-'
  return new Intl.NumberFormat('ru-RU').format(num)
}

const getClosedColor = (isClosed) => {
  const colors = {
    0: 'success',  // Открытая
    1: 'warning',  // Закрытая
    2: 'error'     // Частная
  }
  return colors[isClosed] || 'grey'
}

const getClosedIcon = (isClosed) => {
  const icons = {
    0: 'mdi-lock-open',      // Открытая
    1: 'mdi-lock',           // Закрытая
    2: 'mdi-lock-alert'      // Частная
  }
  return icons[isClosed] || 'mdi-help'
}

const getClosedText = (isClosed) => {
  const texts = {
    0: 'Откр.',    // Открытая
    1: 'Закр.',    // Закрытая
    2: 'Част.'     // Частная
  }
  return texts[isClosed] || '?'
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