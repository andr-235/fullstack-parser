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
import { onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGroupsStore } from '@/stores/groups'
import { storeToRefs } from 'pinia'
import TaskProgress from '@/components/groups/TaskProgress.vue'

const route = useRoute()
const router = useRouter()
const groupsStore = useGroupsStore()
const { currentTask } = storeToRefs(groupsStore)

let pollInterval = null

const taskId = computed(() => route.params.taskId)

const goToGroupsList = () => {
  router.push('/groups')
}

const goToUpload = () => {
  router.push('/groups/upload')
}

const startPolling = () => {
  if (pollInterval) return
  
  pollInterval = setInterval(async () => {
    try {
      const status = await groupsStore.pollTaskStatus(taskId.value)
      if (status.status === 'completed' || status.status === 'failed') {
        clearInterval(pollInterval)
        pollInterval = null
      }
    } catch (error) {
      console.error('Ошибка опроса статуса:', error)
    }
  }, 2000)
}

onMounted(async () => {
  if (taskId.value) {
    try {
      await groupsStore.pollTaskStatus(taskId.value)
      if (currentTask.value?.status === 'processing') {
        startPolling()
      }
    } catch (error) {
      console.error('Ошибка загрузки статуса задачи:', error)
    }
  }
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>
