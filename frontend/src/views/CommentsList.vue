<template>
  <div class="comments-list">
    <h1>Список комментариев</h1>

    <div class="filters">
      <div class="form-group">
        <label for="sentiment">Тональность:</label>
        <select id="sentiment" v-model="filters.sentiment">
          <option value="">all</option>
          <option value="positive">positive</option>
          <option value="neutral">neutral</option>
          <option value="negative">negative</option>
        </select>
      </div>
      <div class="form-group">
        <label for="keyword">Ключевое слово:</label>
        <input
          id="keyword"
          v-model="filters.keyword"
          type="text"
          @input="updateFilters"
        />
      </div>
    </div>

    <div class="pagination">
      <button
        @click="updatePagination(pagination.currentPage - 1)"
        :disabled="pagination.currentPage === 1"
      >
        Предыдущая
      </button>
      <span>Страница {{ pagination.currentPage }} из {{ Math.ceil(commentsStore.pagination.total / pagination.itemsPerPage) }}</span>
      <button
        @click="updatePagination(pagination.currentPage + 1)"
        :disabled="pagination.currentPage * pagination.itemsPerPage >= commentsStore.pagination.total"
      >
        Следующая
      </button>
    </div>

    <LoadingSpinner v-if="commentsStore.loading" />
    <ErrorMessage v-else-if="commentsStore.error" :message="commentsStore.error" />

    <v-data-table
      v-else
      :headers="headers"
      :items="commentsStore.filteredComments"
      :items-per-page="pagination.itemsPerPage"
      :page="pagination.currentPage"
      @update:page="updatePagination"
      class="elevation-1"
    >
    </v-data-table>
  </div>
</template>

<script setup>
import { computed, watch, ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useCommentsStore } from "@/stores/comments";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import ErrorMessage from "@/components/ErrorMessage.vue";

const route = useRoute();
const commentsStore = useCommentsStore();

const taskId = computed(() => route.query.task_id);

const filters = ref({
  sentiment: null,
  keyword: ""
});

const pagination = ref({
  currentPage: 1,
  itemsPerPage: 20
});

const headers = [
  { text: "Текст", value: "text" },
  { text: "Автор", value: "author" },
  { text: "Дата", value: "date" },
  { text: "Тональность", value: "sentiment" }
];

/**
 * Обновляет фильтры и загружает комментарии.
 */
const updateFilters = () => {
  pagination.value.currentPage = 1;
  if (taskId.value) {
    commentsStore.fetchComments(taskId.value, filters.value, pagination.value.currentPage);
  }
};

/**
 * Обновляет пагинацию и загружает комментарии.
 * @param {number} newPage - Новый номер страницы.
 */
const updatePagination = (newPage) => {
  pagination.value.currentPage = newPage;
  if (taskId.value) {
    commentsStore.fetchComments(taskId.value, filters.value, pagination.value.currentPage);
  }
};

watch([taskId, filters, pagination], () => {
  if (taskId.value) {
    commentsStore.fetchComments(taskId.value, filters.value, pagination.value.currentPage);
  }
});

onMounted(() => {
  if (taskId.value) {
    commentsStore.fetchComments(taskId.value, {}, 1);
  }
});
</script>

<style scoped>
.comments-list {
  padding: 20px;
}

.filters {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

button {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>