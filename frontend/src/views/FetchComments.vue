<template>
  <v-container fluid>
    <v-card class="form-card" elevation="2" max-width="600">
      <v-card-title>Создать и запустить задачу</v-card-title>
      <v-card-text>
        <v-form ref="form" @submit.prevent="handleSubmit">
          <v-text-field
            v-model="ownerId"
            label="Owner ID (отрицательный для групп)"
            :rules="ownerIdRules"
            type="number"
            variant="outlined"
            density="compact"
            class="mb-4"
          />
          <v-text-field
            v-model="postId"
            label="Post ID"
            :rules="postIdRules"
            type="number"
            variant="outlined"
            density="compact"
            class="mb-4"
          />
          <v-btn
            type="submit"
            color="primary"
            :loading="loading"
            block
          >
            Создать и запустить
          </v-btn>
        </v-form>
        <LoadingSpinner v-if="loading" class="mt-4" />
      </v-card-text>
    </v-card>
    <v-snackbar
      v-model="showError"
      :color="errorType"
      :text="errorMessage"
      timeout="5000"
      location="top"
    />
  </v-container>
</template>
<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useTasksStore } from '@/stores/tasks';
import LoadingSpinner from '@/components/LoadingSpinner.vue';

import { useLocalStorage } from '@vueuse/core';

/**
 * Компонент формы для создания задачи на сбор комментариев.
 */
const router = useRouter();
const store = useTasksStore();
const form = ref(null);
const loading = ref(false);
const ownerId = ref('');
const postId = ref('');
const errorMessage = ref('');
const errorType = ref('error');
const showError = ref(false);

const ownerIdRules = [
  (v) => !!v || 'Обязательное поле',
  (v) => !isNaN(v) || 'Должно быть числом',
  (v) => true || 'Для групп используйте отрицательное значение'
];
const postIdRules = [
  (v) => !!v || 'Обязательное поле',
  (v) => !isNaN(v) || 'Должно быть числом',
  (v) => v > 0 || 'Должно быть положительным'
];


watch(() => store.errors, (errors) => {
  if (errors.length > 0) {
    errorMessage.value = errors[0];
    showError.value = true;
  }
});

/**
 * Обработка отправки формы.
 * @returns {Promise<void>}
 */
async function handleSubmit() {
  const { valid } = await form.value.validate();
  if (valid) {
    loading.value = true;
    try {
      await store.createTask({
        ownerId: Number(ownerId.value),
        postId: Number(postId.value)
      });
      await store.startCollect(store.taskId);
      router.push(`/tasks/${store.taskId}`);
    } catch (error) {
      errorMessage.value = error.message || 'Ошибка создания задачи';
      showError.value = true;
    } finally {
      loading.value = false;
    }
  }
}
</script>

<style scoped>
.form-card {
  margin: 16px auto;
  padding: 16px;
}
</style>