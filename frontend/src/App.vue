<template>
  <v-app>
    <!-- Sidebar -->
    <AppSidebar />

    <!-- Main Content -->
    <v-main>
      <v-container fluid class="pa-4">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import AppSidebar from "@/components/Sidebar.vue";

/**
 * Корневой компонент приложения с layout на Vuetify.
 * Включает навигацию, проверку токена и обработку роутера.
 */
</script>

<style scoped>
/* Основные стили приложения */
.v-main {
  background-color: #fafafa;
  min-height: 100vh;
}

</style>