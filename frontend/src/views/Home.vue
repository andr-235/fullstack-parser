<template>
  <v-container style="width: 100%;">
    <v-card class="pa-4" elevation="2">
      <v-card-title>
        <h1 class="text-h4 font-weight-bold">Анализ комментариев VK</h1>
      </v-card-title>
      <v-card-text>
        <p>Система для автоматизированного сбора и анализа комментариев из VK API. Мониторинг мнений, выявление ключевых слов и трендов.</p>
      </v-card-text>
      <v-card-actions class="justify-center">
        <router-link to="/fetch">
          <v-btn color="primary" large>Получить комментарии</v-btn>
        </router-link>
        <router-link to="/comments">
          <v-btn color="secondary" large>Просмотреть комментарии</v-btn>
        </router-link>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup>
// Компонент главной страницы
</script>