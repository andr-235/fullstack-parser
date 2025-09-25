<template>
  <v-card class="error-card" elevation="2">
    <v-alert
      :type="alertType"
      :text="message"
      density="compact"
    />
  </v-card>
</template>

<script setup>
/**
 * Компонент для отображения ошибок и предупреждений.
 * @param {string} message - Текст сообщения
 * @param {string} [type='error'] - Тип ('error' или 'warning')
 */
const props = defineProps({
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'error',
    validator: (value) => ['error', 'warning'].includes(value)
  }
});

const alertType = computed(() => props.type);
</script>

<style scoped>
.error-card {
  margin: 16px auto;
  max-width: 600px;
  width: 100%;
}
</style>