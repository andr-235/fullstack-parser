<template>
  <v-card>
    <v-card-title>
      <v-icon class="mr-2">mdi-progress-clock</v-icon>
      Статус обработки
    </v-card-title>
    
    <v-card-text>
      <div class="mb-4">
        <div class="d-flex justify-space-between mb-2">
          <span>Прогресс</span>
          <span>{{ progress.percentage }}%</span>
        </div>
        <v-progress-linear
          :model-value="progress.percentage"
          color="primary"
          height="8"
          rounded
        />
        <div class="text-caption mt-1">
          {{ progress.processed }} из {{ progress.total }} групп
        </div>
      </div>
      
      <v-chip
        :color="getStatusColor(taskStatus.status)"
        class="mb-4"
      >
        {{ getStatusText(taskStatus.status) }}
      </v-chip>
      
      <div v-if="taskStatus.errors && taskStatus.errors.length > 0" class="mt-4">
        <h4>Ошибки валидации:</h4>
        <v-list density="compact">
          <v-list-item
            v-for="error in taskStatus.errors"
            :key="error.groupId"
            class="text-caption"
          >
            <v-list-item-title>ID {{ error.groupId }}: {{ error.error }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  taskStatus: {
    type: Object,
    required: true
  }
})

const progress = computed(() => {
  const { processed = 0, total = 0 } = props.taskStatus.progress || {}
  return {
    processed,
    total,
    percentage: total > 0 ? Math.round((processed / total) * 100) : 0
  }
})

const getStatusColor = (status) => {
  const colors = {
    created: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'error'
  }
  return colors[status] || 'default'
}

const getStatusText = (status) => {
  const texts = {
    created: 'Создана',
    processing: 'Обработка',
    completed: 'Завершена',
    failed: 'Ошибка'
  }
  return texts[status] || status
}
</script>
