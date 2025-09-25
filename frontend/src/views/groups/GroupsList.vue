<template>
  <v-container fluid class="pa-6">
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold">Группы VK</h1>
        <p class="text-body-1 text-medium-emphasis mt-1">
          Управление группами и их статусом
        </p>
      </div>

      <div class="d-flex gap-2">
        <v-btn
          color="primary"
          variant="outlined"
          prepend-icon="mdi-chart-line"
          :to="`/groups/stats/${lastTaskId}`"
          :disabled="!lastTaskId"
        >
          Статистика
        </v-btn>
        <v-btn
          color="primary"
          prepend-icon="mdi-upload"
          to="/groups/upload"
        >
          Загрузить группы
        </v-btn>
      </div>
    </div>

    <v-row>
      <!-- Left Panel - Filters -->
      <v-col cols="12" lg="3">
        <GroupsFiltersPanel />
      </v-col>

      <!-- Right Panel - Table -->
      <v-col cols="12" lg="9">
        <GroupsDataTable @batch-delete="onBatchDelete" />
      </v-col>
    </v-row>

    <!-- Delete Confirmation Dialog -->
    <v-dialog
      v-model="deleteDialog.show"
      max-width="500px"
    >
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon class="me-2" color="error">mdi-alert-circle</v-icon>
          Подтверждение удаления
        </v-card-title>
        <v-card-text>
          <p class="mb-4">
            Вы действительно хотите удалить {{ deleteDialog.count }}
            {{ getGroupsText(deleteDialog.count) }}?
          </p>
          <p class="text-body-2 text-medium-emphasis">
            Это действие необратимо.
          </p>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="deleteDialog.show = false"
            :disabled="deleteDialog.loading"
          >
            Отмена
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            @click="confirmBatchDelete"
            :loading="deleteDialog.loading"
          >
            Удалить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useGroupsStore } from '@/stores/groups'
import GroupsFiltersPanel from '@/components/groups/GroupsFiltersPanel.vue'
import GroupsDataTable from '@/components/groups/GroupsDataTable.vue'

const router = useRouter()
const groupsStore = useGroupsStore()

// Reactive data
const deleteDialog = ref({
  show: false,
  groupIds: [],
  count: 0,
  loading: false
})

// Computed
const lastTaskId = computed(() => {
  // Get last task ID from localStorage or store
  return localStorage.getItem('lastGroupsTaskId') || null
})

// Methods
const onBatchDelete = (groupIds) => {
  deleteDialog.value = {
    show: true,
    groupIds,
    count: groupIds.length,
    loading: false
  }
}

const confirmBatchDelete = async () => {
  deleteDialog.value.loading = true

  try {
    await groupsStore.deleteGroups(deleteDialog.value.groupIds)
    deleteDialog.value.show = false
  } catch (error) {
    console.error('Error deleting groups:', error)
  } finally {
    deleteDialog.value.loading = false
  }
}

const getGroupsText = (count) => {
  const lastDigit = count % 10
  const lastTwoDigits = count % 100

  if (lastTwoDigits >= 11 && lastTwoDigits <= 14) {
    return 'групп'
  }

  if (lastDigit === 1) return 'группу'
  if (lastDigit >= 2 && lastDigit <= 4) return 'группы'
  return 'групп'
}

// Lifecycle
onMounted(() => {
  groupsStore.fetchGroups()
})
</script>
