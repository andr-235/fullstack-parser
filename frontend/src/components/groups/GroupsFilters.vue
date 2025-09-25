<template>
  <v-card class="mb-4">
    <v-card-text>
      <div class="d-flex gap-4">
        <v-select
          v-model="filters.status"
          :items="statusOptions"
          label="Статус"
          style="width: 200px;"
          @update:model-value="updateFilters"
        />
        <v-text-field
          v-model="filters.search"
          label="Поиск по ID или названию"
          prepend-inner-icon="mdi-magnify"
          style="width: 300px;"
          @update:model-value="onSearchChange"
        />
        <v-select
          v-model="filters.sortBy"
          :items="sortOptions"
          label="Сортировка"
          style="width: 200px;"
          @update:model-value="updateFilters"
        />
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { } from 'vue'
import { useGroupsStore } from '@/stores/groups'
import { storeToRefs } from 'pinia'
// Простая реализация debounce без внешних зависимостей
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

const groupsStore = useGroupsStore()
const { filters } = storeToRefs(groupsStore)

const statusOptions = [
  { title: 'Все', value: 'all' },
  { title: 'Валидные', value: 'valid' },
  { title: 'Невалидные', value: 'invalid' },
  { title: 'Дубликаты', value: 'duplicate' }
]

const sortOptions = [
  { title: 'По дате загрузки', value: 'uploadedAt' },
  { title: 'По ID группы', value: 'id' },
  { title: 'По названию', value: 'name' },
  { title: 'По статусу', value: 'status' }
]

const updateFilters = () => {
  groupsStore.updateFilters(filters.value)
}

// Debounced search
const onSearchChange = debounce(() => {
  updateFilters()
}, 500)
</script>
