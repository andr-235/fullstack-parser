<template>
  <v-alert
    v-if="message"
    type="error"
    prominent
    class="mb-4"
  >
    {{ message }}
  </v-alert>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: ''
  }
})
</script>