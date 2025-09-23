<template>
  <v-overlay
    v-if="show"
    contained
    absolute
    opacity="0.8"
  >
    <v-progress-circular
      indeterminate
      color="primary"
      size="64"
    ></v-progress-circular>
    <p v-if="text" class="mt-2 text-h6">{{ text }}</p>
  </v-overlay>
</template>

<script setup>
defineProps({
  show: {
    type: Boolean,
    default: false
  },
  text: {
    type: String,
    default: 'Загрузка...'
  }
})
</script>