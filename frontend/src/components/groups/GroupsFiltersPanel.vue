<template>
  <v-card elevation="2" class="sticky-filters">
    <v-card-title class="d-flex align-center pb-2">
      <v-icon class="me-2" color="primary">mdi-filter-variant</v-icon>
      Фильтры
      <v-spacer />
      <v-btn
        v-if="hasActiveFilters"
        variant="text"
        size="small"
        @click="clearFilters"
      >
        Очистить
      </v-btn>
    </v-card-title>

    <v-card-text class="py-2">
      <!-- Search -->
      <div class="mb-4">
        <v-text-field
          v-model="search"
          label="Поиск по ID/названию"
          variant="outlined"
          density="compact"
          prepend-inner-icon="mdi-magnify"
          clearable
          @update:model-value="debouncedSearch"
        />
      </div>

      <!-- Status Filter -->
      <div class="mb-4">
        <v-select
          v-model="status"
          :items="statusOptions"
          item-title="text"
          item-value="value"
          label="Статус"
          variant="outlined"
          density="compact"
          clearable
          @update:model-value="onFilterChange"
        />
      </div>

      <!-- Date Range Filter -->
      <div class="mb-4">
        <v-expansion-panels variant="accordion" density="compact">
          <v-expansion-panel>
            <v-expansion-panel-title>
              <template #default="{ expanded }">
                <div class="d-flex align-center">
                  <v-icon class="me-2" size="small">
                    mdi-calendar-range
                  </v-icon>
                  <span class="text-body-2">Дата загрузки</span>
                  <v-spacer />
                  <v-chip
                    v-if="dateRange.from || dateRange.to"
                    size="x-small"
                    color="primary"
                    variant="tonal"
                  >
                    Активен
                  </v-chip>
                </div>
              </template>
            </v-expansion-panel-title>
            <v-expansion-panel-text class="pt-2">
              <v-row dense>
                <v-col cols="12">
                  <v-text-field
                    v-model="dateRange.from"
                    label="От"
                    type="date"
                    variant="outlined"
                    density="compact"
                    @update:model-value="onFilterChange"
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="dateRange.to"
                    label="До"
                    type="date"
                    variant="outlined"
                    density="compact"
                    @update:model-value="onFilterChange"
                  />
                </v-col>
              </v-row>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </div>

      <!-- Errors Count Filter -->
      <div class="mb-4">
        <v-expansion-panels variant="accordion" density="compact">
          <v-expansion-panel>
            <v-expansion-panel-title>
              <template #default="{ expanded }">
                <div class="d-flex align-center">
                  <v-icon class="me-2" size="small">
                    mdi-alert-circle-outline
                  </v-icon>
                  <span class="text-body-2">Количество ошибок</span>
                  <v-spacer />
                  <v-chip
                    v-if="errorsCount.min !== null || errorsCount.max !== null"
                    size="x-small"
                    color="primary"
                    variant="tonal"
                  >
                    Активен
                  </v-chip>
                </div>
              </template>
            </v-expansion-panel-title>
            <v-expansion-panel-text class="pt-2">
              <v-row dense>
                <v-col cols="12">
                  <v-text-field
                    v-model="errorsCount.min"
                    label="Минимум"
                    type="number"
                    variant="outlined"
                    density="compact"
                    min="0"
                    @update:model-value="onFilterChange"
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="errorsCount.max"
                    label="Максимум"
                    type="number"
                    variant="outlined"
                    density="compact"
                    min="0"
                    @update:model-value="onFilterChange"
                  />
                </v-col>
              </v-row>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </div>

      <!-- Sort Options -->
      <div class="mb-4">
        <v-expansion-panels variant="accordion" density="compact">
          <v-expansion-panel>
            <v-expansion-panel-title>
              <template #default="{ expanded }">
                <div class="d-flex align-center">
                  <v-icon class="me-2" size="small">
                    mdi-sort
                  </v-icon>
                  <span class="text-body-2">Сортировка</span>
                  <v-spacer />
                  <v-chip
                    v-if="sortBy"
                    size="x-small"
                    color="primary"
                    variant="tonal"
                  >
                    {{ getSortText() }}
                  </v-chip>
                </div>
              </template>
            </v-expansion-panel-title>
            <v-expansion-panel-text class="pt-2">
              <v-select
                v-model="sortBy"
                :items="sortOptions"
                item-title="text"
                item-value="value"
                label="Поле"
                variant="outlined"
                density="compact"
                clearable
                class="mb-2"
                @update:model-value="onFilterChange"
              />
              <v-select
                v-model="sortOrder"
                :items="sortOrderOptions"
                item-title="text"
                item-value="value"
                label="Порядок"
                variant="outlined"
                density="compact"
                :disabled="!sortBy"
                @update:model-value="onFilterChange"
              />
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </div>

      <!-- Statistics -->
      <div class="mb-2">
        <v-card variant="tonal" color="info" class="pa-3">
          <div class="text-body-2">
            <div class="d-flex justify-space-between">
              <span>Всего:</span>
              <strong>{{ totalGroups }}</strong>
            </div>
            <div class="d-flex justify-space-between">
              <span>Показано:</span>
              <strong>{{ displayedGroups }}</strong>
            </div>
            <div v-if="hasActiveFilters" class="d-flex justify-space-between">
              <span>Отфильтровано:</span>
              <strong>{{ filteredGroups }}</strong>
            </div>
          </div>
        </v-card>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useGroupsStore } from '@/stores/groups'

const groupsStore = useGroupsStore()
const { filters, pagination } = storeToRefs(groupsStore)

// Local reactive data
const search = ref(filters.value.search || '')
const status = ref(filters.value.status || '')
const dateRange = ref({
  from: filters.value.dateFrom || '',
  to: filters.value.dateTo || ''
})
const errorsCount = ref({
  min: filters.value.errorsMin !== undefined ? filters.value.errorsMin : null,
  max: filters.value.errorsMax !== undefined ? filters.value.errorsMax : null
})
const sortBy = ref(filters.value.sortBy || '')
const sortOrder = ref(filters.value.sortOrder || 'asc')

// Computed
const hasActiveFilters = computed(() =>
  search.value ||
  status.value ||
  dateRange.value.from ||
  dateRange.value.to ||
  errorsCount.value.min !== null ||
  errorsCount.value.max !== null ||
  sortBy.value
)

const totalGroups = computed(() => pagination.value.total || 0)
const displayedGroups = computed(() => {
  const { page = 1, limit = 20, total = 0 } = pagination.value
  const start = (page - 1) * limit + 1
  const end = Math.min(page * limit, total)
  return total > 0 ? end - start + 1 : 0
})
const filteredGroups = computed(() => totalGroups.value - displayedGroups.value)

// Data
const statusOptions = [
  { text: 'Все статусы', value: '' },
  { text: 'Валидные', value: 'valid' },
  { text: 'Невалидные', value: 'invalid' },
  { text: 'Дубликаты', value: 'duplicate' }
]

const sortOptions = [
  { text: 'ID группы', value: 'groupId' },
  { text: 'Название', value: 'name' },
  { text: 'Статус', value: 'status' },
  { text: 'Дата загрузки', value: 'uploadedAt' },
  { text: 'Последняя проверка', value: 'lastCheckedAt' },
  { text: 'Количество ошибок', value: 'errorsCount' }
]

const sortOrderOptions = [
  { text: 'По возрастанию', value: 'asc' },
  { text: 'По убыванию', value: 'desc' }
]

// Methods
const onFilterChange = () => {
  const newFilters = {
    search: search.value || undefined,
    status: status.value || undefined,
    dateFrom: dateRange.value.from || undefined,
    dateTo: dateRange.value.to || undefined,
    errorsMin: errorsCount.value.min !== null ? parseInt(errorsCount.value.min) : undefined,
    errorsMax: errorsCount.value.max !== null ? parseInt(errorsCount.value.max) : undefined,
    sortBy: sortBy.value || undefined,
    sortOrder: sortOrder.value || 'asc'
  }

  groupsStore.updateFilters(newFilters)
  groupsStore.fetchGroups()
}

// Simple debounce for search
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    onFilterChange()
  }, 500)
}

const clearFilters = () => {
  search.value = ''
  status.value = ''
  dateRange.value = { from: '', to: '' }
  errorsCount.value = { min: null, max: null }
  sortBy.value = ''
  sortOrder.value = 'asc'
  onFilterChange()
}

const getSortText = () => {
  if (!sortBy.value) return ''
  const field = sortOptions.find(opt => opt.value === sortBy.value)?.text || sortBy.value
  const order = sortOrder.value === 'desc' ? '↓' : '↑'
  return `${field} ${order}`
}

// Watch for external filter changes
watch(() => filters.value, (newFilters) => {
  search.value = newFilters.search || ''
  status.value = newFilters.status || ''
  dateRange.value = {
    from: newFilters.dateFrom || '',
    to: newFilters.dateTo || ''
  }
  errorsCount.value = {
    min: newFilters.errorsMin !== undefined ? newFilters.errorsMin : null,
    max: newFilters.errorsMax !== undefined ? newFilters.errorsMax : null
  }
  sortBy.value = newFilters.sortBy || ''
  sortOrder.value = newFilters.sortOrder || 'asc'
}, { deep: true })
</script>

<style scoped>
.sticky-filters {
  position: sticky;
  top: 20px;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
}
</style>