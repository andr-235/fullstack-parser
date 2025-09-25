import { createRouter, createWebHistory } from "vue-router"

/**
 * Создает и конфигурирует роутер Vue.
 * @returns {Object} Экземпляр роутера.
 */
const routes = [
  { path: "/", redirect: "/fetch" },
  {
    path: "/fetch",
    component: () => import("@/views/FetchComments.vue")
  },
  {
    path: "/task/:taskId",
    component: () => import("@/views/TaskStatus.vue")
  },
  {
    path: "/comments",
    component: () => import("@/views/CommentsList.vue")
  },
  // Groups routes
  {
    path: "/groups",
    component: () => import("@/views/groups/GroupsList.vue")
  },
  {
    path: "/groups/upload",
    component: () => import("@/views/groups/GroupsUpload.vue")
  },
  {
    path: "/groups/task/:taskId",
    component: () => import("@/views/groups/GroupsTaskStatus.vue")
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})