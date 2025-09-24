<template>
  <div class="fetch-comments">
    <h1>Получить комментарии</h1>
    <form v-if="!loading && !error" @submit.prevent="submitForm">
      <div class="form-group">
        <label for="ownerId">ID владельца поста:</label>
        <input
          id="ownerId"
          v-model="formData.ownerId"
          type="number"
          required
        />
      </div>
      <div class="form-group">
        <label for="postId">ID поста:</label>
        <input
          id="postId"
          v-model="formData.postId"
          type="number"
          required
        />
      </div>
      <div class="form-group">
        <label for="access_token">Токен доступа VK:</label>
        <input
          id="access_token"
          v-model="formData.access_token"
          type="text"
          required
        />
      </div>
      <button type="submit" :disabled="loading">
        Создать задачу
      </button>
    </form>
    <LoadingSpinner v-else-if="loading" />
    <ErrorMessage v-else-if="error" :message="error" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useTasksStore } from "@/stores/tasks";
import { useSnackbarStore } from "@/stores/snackbar";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import ErrorMessage from "@/components/ErrorMessage.vue";

const router = useRouter();
const tasksStore = useTasksStore();
const snackbarStore = useSnackbarStore();

const formData = ref({
  ownerId: "",
  postId: "",
  access_token: ""
});
const loading = ref(false);
const error = ref(null);

/**
 * Сбрасывает форму.
 */
const resetForm = () => {
  formData.value = {
    ownerId: "",
    postId: "",
    access_token: ""
  };
  error.value = null;
};

onMounted(() => {
  resetForm();
});

/**
 * Отправляет форму для создания задачи.
 * @returns {Promise<void>}
 * @example
 * submitForm();
 */
const submitForm = async () => {
  try {
    loading.value = true;
    error.value = null;
    const taskId = await tasksStore.createTask(formData.value);
    router.push(`/task/${taskId}`);
    snackbarStore.show("Задача создана!");
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};
</script>