<template>
  <div class="register-form">
    <div class="register-form__container">
      <h2 class="register-form__title">Регистрация</h2>

      <!-- Сообщение об ошибке -->
      <div v-if="authStore.error" class="register-form__error">
        <div class="error-message">
          <span class="error-message__icon">⚠️</span>
          <span class="error-message__text">{{ authStore.error.message }}</span>
        </div>
      </div>

      <form @submit.prevent="handleSubmit" class="register-form__form">
        <!-- Поле полное имя -->
        <div class="form-group">
          <label for="fullName" class="form-group__label">
            Полное имя <span class="form-group__required">*</span>
          </label>
          <input
            id="fullName"
            v-model="formData.fullName"
            type="text"
            class="form-group__input"
            :class="{ 'form-group__input--error': errors.fullName }"
            placeholder="Введите ваше полное имя"
            required
            autocomplete="name"
          />
          <div v-if="errors.fullName" class="form-group__error">
            {{ errors.fullName }}
          </div>
        </div>

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
              placeholder="Введите пароль"
              required
              autocomplete="new-password"
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
          <!-- Индикатор сложности пароля -->
          <div v-if="formData.password" class="password-strength">
            <div class="password-strength__bar">
              <div
                class="password-strength__fill"
                :class="passwordStrengthClass"
                :style="{ width: passwordStrengthPercent + '%' }"
              ></div>
            </div>
            <span class="password-strength__text" :class="passwordStrengthClass">
              {{ passwordStrengthText }}
            </span>
          </div>
        </div>

        <!-- Поле подтверждение пароля -->
        <div class="form-group">
          <label for="confirmPassword" class="form-group__label">
            Подтвердите пароль <span class="form-group__required">*</span>
          </label>
          <div class="form-group__password-wrapper">
            <input
              id="confirmPassword"
              v-model="formData.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              class="form-group__input"
              :class="{ 'form-group__input--error': errors.confirmPassword }"
              placeholder="Повторите пароль"
              required
              autocomplete="new-password"
            />
            <button
              type="button"
              class="form-group__password-toggle"
              @click="showConfirmPassword = !showConfirmPassword"
              tabindex="-1"
            >
              <span v-if="showConfirmPassword">🙈</span>
              <span v-else>👁️</span>
            </button>
          </div>
          <div v-if="errors.confirmPassword" class="form-group__error">
            {{ errors.confirmPassword }}
          </div>
        </div>

        <!-- Чекбокс согласия -->
        <div class="form-group">
          <label class="form-group__checkbox-label">
            <input
              v-model="formData.agreeToTerms"
              type="checkbox"
              class="form-group__checkbox"
              :class="{ 'form-group__checkbox--error': errors.agreeToTerms }"
            />
            <span class="form-group__checkbox-text">
              Я согласен с
              <router-link to="/terms" class="form-group__link" target="_blank">
                условиями использования
              </router-link>
              и
              <router-link to="/privacy" class="form-group__link" target="_blank">
                политикой конфиденциальности
              </router-link>
              <span class="form-group__required">*</span>
            </span>
          </label>
          <div v-if="errors.agreeToTerms" class="form-group__error">
            {{ errors.agreeToTerms }}
          </div>
        </div>

        <!-- Кнопка регистрации -->
        <button
          type="submit"
          class="register-form__submit"
          :disabled="authStore.isLoading || !isFormValid"
        >
          <span v-if="authStore.isLoading" class="register-form__loading">
            <span class="loading-spinner"></span>
            Регистрация...
          </span>
          <span v-else>Зарегистрироваться</span>
        </button>
      </form>

      <!-- Ссылки -->
      <div class="register-form__links">
        <router-link to="/auth/login" class="register-form__link">
          Уже есть аккаунт? Войти
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth.store";

/**
 * Интерфейс для данных формы регистрации
 */
interface RegisterFormData {
  fullName: string;
  email: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: boolean;
}

/**
 * Интерфейс для ошибок валидации
 */
interface FormErrors {
  fullName?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  agreeToTerms?: string;
}

// Composables
const router = useRouter();
const authStore = useAuthStore();

// Реактивные данные
const showPassword = ref<boolean>(false);
const showConfirmPassword = ref<boolean>(false);
const formData = reactive<RegisterFormData>({
  fullName: "",
  email: "",
  password: "",
  confirmPassword: "",
  agreeToTerms: false
});

const errors = reactive<FormErrors>({});

// Вычисляемые свойства
const isFormValid = computed<boolean>(() => {
  return !!(
    formData.fullName &&
    formData.email &&
    formData.password &&
    formData.confirmPassword &&
    formData.agreeToTerms &&
    !errors.fullName &&
    !errors.email &&
    !errors.password &&
    !errors.confirmPassword &&
    !errors.agreeToTerms
  );
});

const passwordStrength = computed<number>(() => {
  const password = formData.password;
  if (!password) return 0;

  let score = 0;

  // Длина пароля
  if (password.length >= 8) score += 25;
  else if (password.length >= 6) score += 15;

  // Содержит строчные буквы
  if (/[a-z]/.test(password)) score += 25;

  // Содержит заглавные буквы
  if (/[A-Z]/.test(password)) score += 25;

  // Содержит цифры
  if (/\d/.test(password)) score += 15;

  // Содержит специальные символы
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) score += 10;

  return Math.min(score, 100);
});

const passwordStrengthClass = computed<string>(() => {
  const strength = passwordStrength.value;
  if (strength < 30) return "password-strength--weak";
  if (strength < 60) return "password-strength--medium";
  if (strength < 80) return "password-strength--strong";
  return "password-strength--very-strong";
});

const passwordStrengthText = computed<string>(() => {
  const strength = passwordStrength.value;
  if (strength < 30) return "Слабый";
  if (strength < 60) return "Средний";
  if (strength < 80) return "Сильный";
  return "Очень сильный";
});

const passwordStrengthPercent = computed<number>(() => {
  return passwordStrength.value;
});

// Методы
const validateFullName = (name: string): boolean => {
  if (!name.trim()) {
    errors.fullName = "Полное имя обязательно для заполнения";
    return false;
  }
  if (name.trim().length < 2) {
    errors.fullName = "Полное имя должно содержать минимум 2 символа";
    return false;
  }
  if (name.trim().length > 100) {
    errors.fullName = "Полное имя не может превышать 100 символов";
    return false;
  }
  return true;
};

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
  if (password.length < 8) {
    errors.password = "Пароль должен содержать минимум 8 символов";
    return false;
  }
  if (password.length > 128) {
    errors.password = "Пароль не может превышать 128 символов";
    return false;
  }
  return true;
};

const validateConfirmPassword = (confirmPassword: string): boolean => {
  if (!confirmPassword) {
    errors.confirmPassword = "Подтверждение пароля обязательно";
    return false;
  }
  if (confirmPassword !== formData.password) {
    errors.confirmPassword = "Пароли не совпадают";
    return false;
  }
  return true;
};

const validateAgreeToTerms = (agree: boolean): boolean => {
  if (!agree) {
    errors.agreeToTerms = "Необходимо согласиться с условиями использования";
    return false;
  }
  return true;
};

const validateForm = (): boolean => {
  const isFullNameValid = validateFullName(formData.fullName);
  const isEmailValid = validateEmail(formData.email);
  const isPasswordValid = validatePassword(formData.password);
  const isConfirmPasswordValid = validateConfirmPassword(formData.confirmPassword);
  const isAgreeToTermsValid = validateAgreeToTerms(formData.agreeToTerms);

  // Очищаем ошибки для полей, которые прошли валидацию
  if (isFullNameValid) delete errors.fullName;
  if (isEmailValid) delete errors.email;
  if (isPasswordValid) delete errors.password;
  if (isConfirmPasswordValid) delete errors.confirmPassword;
  if (isAgreeToTermsValid) delete errors.agreeToTerms;

  return isFullNameValid && isEmailValid && isPasswordValid &&
         isConfirmPasswordValid && isAgreeToTermsValid;
};

const handleSubmit = async (): Promise<void> => {
  if (!validateForm()) {
    return;
  }

  try {
    const success = await authStore.register(
      formData.email,
      formData.password,
      formData.fullName
    );

    if (success) {
      // Перенаправляем на страницу подтверждения или главную
      await router.push({
        name: "register-success",
        query: { email: formData.email }
      });
    }
  } catch (error) {
    console.error("Ошибка регистрации:", error);
  }
};

// Lifecycle
onMounted(() => {
  // Предварительно заполняем email из query параметров, если есть
  const route = useRouter().currentRoute.value;
  if (route.query.email) {
    formData.email = route.query.email as string;
  }
});
</script>

<style scoped>
.register-form {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-form__container {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
}

.register-form__title {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
  font-size: 1.75rem;
  font-weight: 600;
}

.register-form__error {
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

.register-form__form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group__label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
}

.form-group__required {
  color: #e74c3c;
}

.form-group__input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
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

.password-strength {
  margin-top: 0.5rem;
}

.password-strength__bar {
  width: 100%;
  height: 4px;
  background-color: #e1e5e9;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.password-strength__fill {
  height: 100%;
  transition: all 0.3s ease;
}

.password-strength--weak {
  background-color: #e74c3c;
}

.password-strength--medium {
  background-color: #f39c12;
}

.password-strength--strong {
  background-color: #f1c40f;
}

.password-strength--very-strong {
  background-color: #27ae60;
}

.password-strength__text {
  font-size: 0.75rem;
  font-weight: 500;
}

.password-strength--weak {
  color: #e74c3c;
}

.password-strength--medium {
  color: #f39c12;
}

.password-strength--strong {
  color: #f1c40f;
}

.password-strength--very-strong {
  color: #27ae60;
}

.form-group__checkbox-label {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
  font-weight: normal;
}

.form-group__checkbox {
  margin-right: 0.5rem;
  margin-top: 0.125rem;
  width: 1rem;
  height: 1rem;
  accent-color: #667eea;
}

.form-group__checkbox--error + .form-group__checkbox-text {
  color: #e74c3c;
}

.form-group__checkbox-text {
  flex: 1;
  line-height: 1.4;
  font-size: 0.9rem;
  color: #666;
}

.form-group__link {
  color: #667eea;
  text-decoration: none;
}

.form-group__link:hover {
  text-decoration: underline;
}

.register-form__submit {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.875rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-top: 0.5rem;
}

.register-form__submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.register-form__submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.register-form__loading {
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

.register-form__links {
  margin-top: 2rem;
  text-align: center;
}

.register-form__link {
  color: #667eea;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.register-form__link:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* Адаптивность */
@media (max-width: 480px) {
  .register-form {
    padding: 1rem;
  }

  .register-form__container {
    padding: 2rem 1.5rem;
  }

  .register-form__title {
    font-size: 1.5rem;
  }

  .form-group__checkbox-text {
    font-size: 0.8rem;
  }
}
</style>