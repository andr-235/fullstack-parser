<template>
  <div class="pa-6">
    <div class="d-flex justify-center">
      <div style="width: 600px;">
        <h1 class="text-h4 mb-6">Статус обработки групп</h1>
        
        <TaskProgress :task-status="currentTask" />
        
        <v-card v-if="currentTask?.status === 'completed'" class="mt-4">
          <v-card-title>
            <v-icon class="mr-2">mdi-check-circle</v-icon>
            Обработка завершена
          </v-card-title>
          <v-card-text>
            <v-btn
              color="primary"
              @click="goToGroupsList"
            >
              Перейти к списку групп
            </v-btn>
          </v-card-text>
        </v-card>
        
        <v-card v-if="currentTask?.status === 'failed'" class="mt-4">
          <v-card-title>
            <v-icon class="mr-2" color="error">mdi-alert-circle</v-icon>
            Ошибка обработки
          </v-card-title>
          <v-card-text>
            <v-btn
              color="primary"
              @click="goToUpload"
            >
              Попробовать снова
            </v-btn>
          </v-card-text>
        </v-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGroupsStore } from '@/stores/groups'
import { useAdaptivePolling } from '@/composables/useAdaptivePolling'
import { groupsApi } from '@/services/api'
import { storeToRefs } from 'pinia'
import TaskProgress from '@/components/groups/TaskProgress.vue'

const route = useRoute()
const router = useRouter()
const groupsStore = useGroupsStore()

const taskId = computed(() => route.params.taskId)
const currentTask = ref(null)

// Адаптивный polling для статуса задачи групп
const polling = useAdaptivePolling(
  taskId,
  'general' // Для статуса задач групп используем general конфигурацию
)

const goToGroupsList = () => {
  router.push('/groups')
}

const goToUpload = () => {
  router.push('/groups/upload')
}

onMounted(async () => {
  if (taskId.value) {
    try {
      // Получаем первоначальный статус задачи
      const response = await groupsApi.getTaskStatus(taskId.value)
      currentTask.value = response.data.data

      // Запускаем адаптивный polling если задача выполняется
      if (['pending', 'processing'].includes(currentTask.value?.status)) {
        await polling.startPolling(async () => {
          const statusResponse = await groupsApi.getTaskStatus(taskId.value)
          currentTask.value = statusResponse.data.data
          return {
            status: statusResponse.data.data.status,
            progress: statusResponse.data.data.progress,
            ...statusResponse.data.data
          }
        })
      }
    } catch (error) {
      console.error('Ошибка загрузки статуса задачи:', error)
    }
  }
})

onUnmounted(() => {
  polling.stopPolling()
})
</script>
