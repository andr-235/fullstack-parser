<template>
  <div class="task-status">
    <h1>Статус задачи {{ taskId }}</h1>
    <LoadingSpinner v-if="loading" />
    <ErrorMessage v-else-if="tasksStore.currentTask.error" :message="tasksStore.currentTask.error" />
    <div v-else>
      <p>Статус: {{ tasksStore.getFormattedStatus }}</p>
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: tasksStore.currentTask.progress + '%' }"
        ></div>
      </div>
      <p>Прогресс: {{ tasksStore.currentTask.progress }}%</p>
      <button 
        v-if="tasksStore.currentTask.status === 'completed'" 
        @click="goToComments"
      >
        К комментариям
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useTasksStore } from "@/stores/tasks";
import { useSnackbarStore } from "@/stores/snackbar";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import ErrorMessage from "@/components/ErrorMessage.vue";

const route = useRoute();
const router = useRouter();
const tasksStore = useTasksStore();
const snackbarStore = useSnackbarStore();

const taskId = route.params.id;
const loading = ref(false);
const intervalId = ref(null);

/**
 * Переходит к комментариям.
 */
const goToComments = () => {
  router.push(`/comments?task_id=${taskId}`);
};

onMounted(async () => {
  loading.value = true;
  await tasksStore.fetchStatus(taskId);
  loading.value = false;
  intervalId.value = setInterval(async () => {
    await tasksStore.fetchStatus(taskId);
    if (tasksStore.currentTask.status === "completed") {
      router.push(`/comments?task_id=${taskId}`);
      snackbarStore.show("Анализ завершён!");
      clearInterval(intervalId.value);
    }
  }, 5000);
});

onUnmounted(() => {
  if (intervalId.value) {
    clearInterval(intervalId.value);
  }
});
</script>

<style scoped>
.progress-bar {
  width: 100%;
  height: 20px;
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #4caf50;
  transition: width 0.3s ease;
}
</style>