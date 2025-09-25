<template>
  <v-card style="width: 100%;">
    <v-card-title class="d-flex justify-space-between align-center">
      <span>Список групп ({{ pagination.total }})</span>
      <v-btn
        color="primary"
        prepend-icon="mdi-plus"
        @click="$emit('upload')"
      >
        Загрузить группы
      </v-btn>
    </v-card-title>
    
    <v-data-table
      :headers="headers"
      :items="groups"
      :loading="loading"
      :items-per-page="pagination.limit"
      :page="pagination.page"
      @update:page="onPageChange"
      @update:items-per-page="onItemsPerPageChange"
    >
      <template #[`item.status`]="{ item }">
        <v-chip
          :color="getStatusColor(item.status)"
          size="small"
        >
          {{ getStatusText(item.status) }}
        </v-chip>
      </template>
      
      <template #[`item.actions`]="{ item }">
        <v-btn
          color="error"
          size="small"
          variant="outlined"
          @click="deleteGroup(item.id)"
        >
          <template #prepend>
            <v-icon>mdi-delete</v-icon>
          </template>
          Удалить
        </v-btn>
      </template>
    </v-data-table>
  </v-card>
</template>

<script setup>
import { useGroupsStore } from '@/stores/groups'
import { storeToRefs } from 'pinia'

defineEmits(['upload'])

const groupsStore = useGroupsStore()
const { groups, loading, pagination } = storeToRefs(groupsStore)

const headers = [
  { title: 'ID группы', key: 'id', sortable: true },
  { title: 'Название', key: 'name', sortable: true },
  { title: 'Статус', key: 'status', sortable: true },
  { title: 'Дата загрузки', key: 'uploadedAt', sortable: true },
  { title: 'Действия', key: 'actions', sortable: false }
]

const getStatusColor = (status) => {
  const colors = {
    valid: 'success',
    invalid: 'error',
    duplicate: 'warning'
  }
  return colors[status] || 'default'
}

const getStatusText = (status) => {
  const texts = {
    valid: 'Валидная',
    invalid: 'Невалидная',
    duplicate: 'Дубликат'
  }
  return texts[status] || status
}

const deleteGroup = async (groupId) => {
  if (confirm('Удалить группу?')) {
    await groupsStore.deleteGroup(groupId)
  }
}

const onPageChange = (page) => {
  groupsStore.updateFilters({ page })
}

const onItemsPerPageChange = (limit) => {
  groupsStore.updateFilters({ limit, page: 1 })
}
</script>
