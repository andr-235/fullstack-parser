<template>
  <div class="login-form">
    <div class="login-form__container">
      <h2 class="login-form__title">Вход в систему</h2>

      <!-- Сообщение об ошибке -->
      <div v-if="authStore.error" class="login-form__error">
        <div class="error-message">
          <span class="error-message__icon">⚠️</span>
          <span class="error-message__text">{{ authStore.error.message }}</span>
        </div>
      </div>

      <form @submit.prevent="handleSubmit" class="login-form__form">
        <!-- Поле email -->
        <div class="form-group">
          <label for="email" class="form-group__label">
            Email <span class="form-group__required">*</span>
          </label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            class="form-group__input"
            :class="{ 'form-group__input--error': errors.email }"
            placeholder="Введите ваш email"
            required
            autocomplete="email"
          />
          <div v-if="errors.email" class="form-group__error">
            {{ errors.email }}
          </div>
        </div>

        <!-- Поле пароль -->
        <div class="form-group">
          <label for="password" class="form-group__label">
            Пароль <span class="form-group__required">*</span>
          </label>
          <div class="form-group__password-wrapper">
            <input
              id="password"
              v-model="formData.password"
              :type="showPassword ? 'text' : 'password'"
              class="form-group__input"
              :class="{ 'form-group__input--error': errors.password }"
              placeholder="Введите ваш пароль"
              required
              autocomplete="current-password"
            />
            <button
              type="button"
              class="form-group__password-toggle"
              @click="showPassword = !showPassword"
              tabindex="-1"
            >
              <span v-if="showPassword">🙈</span>
              <span v-else>👁️</span>
            </button>
          </div>
          <div v-if="errors.password" class="form-group__error">
            {{ errors.password }}
          </div>
        </div>

        <!-- Кнопка входа -->
        <button
          type="submit"
          class="login-form__submit"
          :disabled="authStore.isLoading || !isFormValid"
        >
          <span v-if="authStore.isLoading" class="login-form__loading">
            <span class="loading-spinner"></span>
            Вход...
          </span>
          <span v-else>Войти</span>
        </button>
      </form>

      <!-- Ссылки -->
      <div class="login-form__links">
        <router-link to="/auth/forgot-password" class="login-form__link">
          Забыли пароль?
        </router-link>
        <router-link to="/auth/register" class="login-form__link">
          Нет аккаунта? Зарегистрироваться
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "../stores/auth.store";

/**
 * Интерфейс для данных формы входа
 */
interface LoginFormData {
  email: string;
  password: string;
}

/**
 * Интерфейс для ошибок валидации
 */
interface FormErrors {
  email?: string;
  password?: string;
}

// Composables
const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

// Реактивные данные
const showPassword = ref<boolean>(false);
const formData = reactive<LoginFormData>({
  email: "",
  password: ""
});

const errors = reactive<FormErrors>({});

// Вычисляемые свойства
const isFormValid = computed<boolean>(() => {
  return !!(formData.email && formData.password && !errors.email && !errors.password);
});

// Методы
const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email) {
    errors.email = "Email обязателен для заполнения";
    return false;
  }
  if (!emailRegex.test(email)) {
    errors.email = "Введите корректный email адрес";
    return false;
  }
  return true;
};

const validatePassword = (password: string): boolean => {
  if (!password) {
    errors.password = "Пароль обязателен для заполнения";
    return false;
  }
  if (password.length < 6) {
    errors.password = "Пароль должен содержать минимум 6 символов";
    return false;
  }
  return true;
};

const validateForm = (): boolean => {
  const isEmailValid = validateEmail(formData.email);
  const isPasswordValid = validatePassword(formData.password);

  // Очищаем ошибки для полей, которые прошли валидацию
  if (isEmailValid) {
    delete errors.email;
  }
  if (isPasswordValid) {
    delete errors.password;
  }

  return isEmailValid && isPasswordValid;
};

const handleSubmit = async (): Promise<void> => {
  if (!validateForm()) {
    return;
  }

  try {
    const success = await authStore.login(formData.email, formData.password);

    if (success) {
      // Перенаправляем пользователя на целевую страницу или главную
      const redirectTo = (route.query.redirect as string) || "/";
      await router.push(redirectTo);
    }
  } catch (error) {
    console.error("Ошибка входа:", error);
  }
};

// Lifecycle
onMounted(() => {
  // Предварительно заполняем email из query параметров, если есть
  if (route.query.email) {
    formData.email = route.query.email as string;
  }
});
</script>

<style scoped>
.login-form {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100%;
  padding: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-form__container {
  background: white;
  padding: 3.5rem;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 500px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-form__title {
  text-align: center;
  margin-bottom: 2.5rem;
  color: #333;
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.login-form__error {
  margin-bottom: 1.5rem;
}

.error-message {
  display: flex;
  align-items: center;
  padding: 1rem;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  color: #c33;
}

.error-message__icon {
  margin-right: 0.5rem;
  font-size: 1.1rem;
}

.error-message__text {
  flex: 1;
}

.login-form__form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-group__label {
  display: block;
  margin-bottom: 0.75rem;
  color: #555;
  font-weight: 600;
  font-size: 1.1rem;
}

.form-group__required {
  color: #e74c3c;
}

.form-group__input {
  width: 100%;
  padding: 1rem 1.25rem;
  border: 2px solid #e1e5e9;
  border-radius: 10px;
  font-size: 1.1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.form-group__input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group__input--error {
  border-color: #e74c3c;
}

.form-group__input--error:focus {
  border-color: #e74c3c;
  box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
}

.form-group__password-wrapper {
  position: relative;
}

.form-group__password-toggle {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.form-group__password-toggle:hover {
  background-color: #f0f0f0;
}

.form-group__error {
  margin-top: 0.25rem;
  color: #e74c3c;
  font-size: 0.875rem;
}

.login-form__submit {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1.125rem 2rem;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-top: 1rem;
}

.login-form__submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.login-form__submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.login-form__loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.login-form__links {
  margin-top: 2.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.login-form__link {
  color: #667eea;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
  transition: color 0.2s;
}

.login-form__link:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* Десктопные стили для экранов >1024px */
@media (min-width: 1024px) {
  .login-form {
    padding: 0;
  }

  .login-form__container {
    max-width: 600px;
    padding: 4rem;
  }

  .login-form__title {
    font-size: 2.25rem;
    margin-bottom: 3rem;
  }

  .login-form__form {
    gap: 2.5rem;
  }

  .form-group__label {
    font-size: 1.2rem;
    margin-bottom: 1rem;
  }

  .form-group__input {
    padding: 1.25rem 1.5rem;
    font-size: 1.2rem;
  }

  .login-form__submit {
    padding: 1.25rem 2.5rem;
    font-size: 1.2rem;
    margin-top: 1.5rem;
  }

  .login-form__links {
    margin-top: 3rem;
    gap: 1.5rem;
  }

  .login-form__link {
    font-size: 1.1rem;
  }
}
</style>