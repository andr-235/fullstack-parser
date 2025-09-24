import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

import { LoginForm, RegisterForm, ChangePasswordForm } from '../auth/components'
console.log('LoginForm imported:', typeof LoginForm);

// Импорт guards аутентификации
import { authGuard } from '../auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
      meta: {
        requiresAuth: true
      }
    },

    // Роуты аутентификации
    {
      path: '/auth/login',
      name: 'login',
      component: LoginForm,
      meta: {
        requiresGuest: true,
        title: 'Вход в систему'
      }
    },
    {
      path: '/auth/register',
      name: 'register',
      component: RegisterForm,
      meta: {
        requiresGuest: true,
        title: 'Регистрация'
      }
    },
    {
      path: '/auth/change-password',
      name: 'change-password',
      component: ChangePasswordForm,
      meta: {
        requiresAuth: true,
        title: 'Смена пароля'
      }
    },
    {
      path: '/auth/register-success',
      name: 'register-success',
      component: () => import('../auth/components/RegisterSuccess.vue'),
      meta: {
        title: 'Регистрация завершена'
      }
    },

    // Защищенные роуты с проверкой ролей
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
      meta: {
        requiresAuth: true,
        requiredRoles: ['admin'],
        title: 'Панель администратора'
      }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: {
        requiresAuth: true,
        title: 'Профиль пользователя'
      }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: HomeView,
      meta: {
        requiresAuth: true,
        title: 'Dashboard'
      }
    },
    {
      path: '/posts',
      name: 'posts',
      component: () => import('../views/PostsView.vue'),
      meta: {
        requiresAuth: true,
        title: 'Посты'
      }
    },
    {
      path: '/authors',
      name: 'authors',
      component: () => import('../views/AuthorsView.vue'),
      meta: {
        requiresAuth: true,
        title: 'Авторы'
      }
    },
    {
      path: '/groups',
      name: 'groups',
      component: () => import('../views/GroupsView.vue'),
      meta: {
        requiresAuth: true,
        title: 'Группы'
      }
    },
    {
      path: '/logout',
      name: 'logout',
      redirect: '/auth/login'
    },

    // Обработка ошибок
    {
      path: '/unauthorized',
      name: 'unauthorized',
      component: () => import('../views/UnauthorizedView.vue'),
      meta: {
        title: 'Доступ запрещен'
      }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue'),
      meta: {
        title: 'Страница не найдена'
      }
    }
  ],
})

// Глобальные guards
router.beforeEach(authGuard)

export default router
