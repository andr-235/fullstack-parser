<template>
  <div class="change-password-form">
    <div class="change-password-form__container">
      <h2 class="change-password-form__title">Смена пароля</h2>

      <!-- Сообщение об ошибке -->
      <div v-if="authStore.error" class="change-password-form__error">
        <div class="error-message">
          <span class="error-message__icon">⚠️</span>
          <span class="error-message__text">{{ authStore.error.message }}</span>
        </div>
      </div>

      <!-- Сообщение об успехе -->
      <div v-if="successMessage" class="change-password-form__success">
        <div class="success-message">
          <span class="success-message__icon">✅</span>
          <span class="success-message__text">{{ successMessage }}</span>
        </div>
      </div>

      <form @submit.prevent="handleSubmit" class="change-password-form__form">
        <!-- Текущий пароль -->
        <div class="form-group">
          <label for="currentPassword" class="form-group__label">
            Текущий пароль <span class="form-group__required">*</span>
          </label>
          <div class="form-group__password-wrapper">
            <input
              id="currentPassword"
              v-model="formData.currentPassword"
              :type="showCurrentPassword ? 'text' : 'password'"
              class="form-group__input"
              :class="{ 'form-group__input--error': errors.currentPassword }"
              placeholder="Введите текущий пароль"
              required
              autocomplete="current-password"
            />
            <button
              type="button"
              class="form-group__password-toggle"
              @click="showCurrentPassword = !showCurrentPassword"
              tabindex="-1"
            >
              <span v-if="showCurrentPassword">🙈</span>
              <span v-else>👁️</span>
            </button>
          </div>
          <div v-if="errors.currentPassword" class="form-group__error">
            {{ errors.currentPassword }}
          </div>
        </div>

        <!-- Новый пароль -->
        <div class="form-group">
          <label for="newPassword" class="form-group__label">
            Новый пароль <span class="form-group__required">*</span>
          </label>
          <div class="form-group__password-wrapper">
            <input
              id="newPassword"
              v-model="formData.newPassword"
              :type="showNewPassword ? 'text' : 'password'"
              class="form-group__input"
              :class="{ 'form-group__input--error': errors.newPassword }"
              placeholder="Введите новый пароль"
              required
              autocomplete="new-password"
            />
            <button
              type="button"
              class="form-group__password-toggle"
              @click="showNewPassword = !showNewPassword"
              tabindex="-1"
            >
              <span v-if="showNewPassword">🙈</span>
              <span v-else>👁️</span>
            </button>
          </div>
          <div v-if="errors.newPassword" class="form-group__error">
            {{ errors.newPassword }}
          </div>
          <!-- Индикатор сложности пароля -->
          <div v-if="formData.newPassword" class="password-strength">
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

        <!-- Подтверждение нового пароля -->
        <div class="form-group">
          <label for="confirmNewPassword" class="form-group__label">
            Подтвердите новый пароль <span class="form-group__required">*</span>
          </label>
          <div class="form-group__password-wrapper">
            <input
              id="confirmNewPassword"
              v-model="formData.confirmNewPassword"
              :type="showConfirmNewPassword ? 'text' : 'password'"
              class="form-group__input"
              :class="{ 'form-group__input--error': errors.confirmNewPassword }"
              placeholder="Повторите новый пароль"
              required
              autocomplete="new-password"
            />
            <button
              type="button"
              class="form-group__password-toggle"
              @click="showConfirmNewPassword = !showConfirmNewPassword"
              tabindex="-1"
            >
              <span v-if="showConfirmNewPassword">🙈</span>
              <span v-else>👁️</span>
            </button>
          </div>
          <div v-if="errors.confirmNewPassword" class="form-group__error">
            {{ errors.confirmNewPassword }}
          </div>
        </div>

        <!-- Кнопка смены пароля -->
        <button
          type="submit"
          class="change-password-form__submit"
          :disabled="authStore.isLoading || !isFormValid"
        >
          <span v-if="authStore.isLoading" class="change-password-form__loading">
            <span class="loading-spinner"></span>
            Смена пароля...
          </span>
          <span v-else>Сменить пароль</span>
        </button>
      </form>

      <!-- Дополнительные действия -->
      <div class="change-password-form__actions">
        <router-link to="/auth/forgot-password" class="change-password-form__link">
          Забыли пароль?
        </router-link>
        <button
          type="button"
          class="change-password-form__link change-password-form__link--button"
          @click="generateSecurePassword"
        >
          Сгенерировать безопасный пароль
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth.store";

/**
 * Интерфейс для данных формы смены пароля
 */
interface ChangePasswordFormData {
  currentPassword: string;
  newPassword: string;
  confirmNewPassword: string;
}

/**
 * Интерфейс для ошибок валидации
 */
interface FormErrors {
  currentPassword?: string;
  newPassword?: string;
  confirmNewPassword?: string;
}

// Composables
const router = useRouter();
const authStore = useAuthStore();

// Реактивные данные
const showCurrentPassword = ref<boolean>(false);
const showNewPassword = ref<boolean>(false);
const showConfirmNewPassword = ref<boolean>(false);
const successMessage = ref<string>("");

const formData = reactive<ChangePasswordFormData>({
  currentPassword: "",
  newPassword: "",
  confirmNewPassword: ""
});

const errors = reactive<FormErrors>({});

// Вычисляемые свойства
const isFormValid = computed<boolean>(() => {
  return !!(
    formData.currentPassword &&
    formData.newPassword &&
    formData.confirmNewPassword &&
    !errors.currentPassword &&
    !errors.newPassword &&
    !errors.confirmNewPassword
  );
});

const passwordStrength = computed<number>(() => {
  const password = formData.newPassword;
  if (!password) return 0;

  let score = 0;

  // Длина пароля
  if (password.length >= 12) score += 30;
  else if (password.length >= 8) score += 20;
  else if (password.length >= 6) score += 10;

  // Содержит строчные буквы
  if (/[a-z]/.test(password)) score += 20;

  // Содержит заглавные буквы
  if (/[A-Z]/.test(password)) score += 20;

  // Содержит цифры
  if (/\d/.test(password)) score += 15;

  // Содержит специальные символы
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) score += 15;

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
const validateCurrentPassword = (password: string): boolean => {
  if (!password) {
    errors.currentPassword = "Текущий пароль обязателен для заполнения";
    return false;
  }
  if (password.length < 6) {
    errors.currentPassword = "Текущий пароль должен содержать минимум 6 символов";
    return false;
  }
  return true;
};

const validateNewPassword = (password: string): boolean => {
  if (!password) {
    errors.newPassword = "Новый пароль обязателен для заполнения";
    return false;
  }
  if (password.length < 8) {
    errors.newPassword = "Новый пароль должен содержать минимум 8 символов";
    return false;
  }
  if (password.length > 128) {
    errors.newPassword = "Новый пароль не может превышать 128 символов";
    return false;
  }
  if (password === formData.currentPassword) {
    errors.newPassword = "Новый пароль должен отличаться от текущего";
    return false;
  }
  return true;
};

const validateConfirmNewPassword = (confirmPassword: string): boolean => {
  if (!confirmPassword) {
    errors.confirmNewPassword = "Подтверждение пароля обязательно";
    return false;
  }
  if (confirmPassword !== formData.newPassword) {
    errors.confirmNewPassword = "Пароли не совпадают";
    return false;
  }
  return true;
};

const validateForm = (): boolean => {
  const isCurrentPasswordValid = validateCurrentPassword(formData.currentPassword);
  const isNewPasswordValid = validateNewPassword(formData.newPassword);
  const isConfirmNewPasswordValid = validateConfirmNewPassword(formData.confirmNewPassword);

  // Очищаем ошибки для полей, которые прошли валидацию
  if (isCurrentPasswordValid) delete errors.currentPassword;
  if (isNewPasswordValid) delete errors.newPassword;
  if (isConfirmNewPasswordValid) delete errors.confirmNewPassword;

  return isCurrentPasswordValid && isNewPasswordValid && isConfirmNewPasswordValid;
};

const handleSubmit = async (): Promise<void> => {
  if (!validateForm()) {
    return;
  }

  try {
    const success = await authStore.changePassword(
      formData.currentPassword,
      formData.newPassword
    );

    if (success) {
      successMessage.value = "Пароль успешно изменен!";
      // Очищаем форму
      formData.currentPassword = "";
      formData.newPassword = "";
      formData.confirmNewPassword = "";

      // Скрываем сообщение об успехе через 5 секунд
      setTimeout(() => {
        successMessage.value = "";
      }, 5000);
    }
  } catch (error) {
    console.error("Ошибка смены пароля:", error);
  }
};

const generateSecurePassword = (): void => {
  const length = 16;
  const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?";

  let password = "";
  for (let i = 0; i < length; i++) {
    password += charset.charAt(Math.floor(Math.random() * charset.length));
  }

  formData.newPassword = password;
  formData.confirmNewPassword = password;

  // Очищаем ошибки
  delete errors.newPassword;
  delete errors.confirmNewPassword;
};

// Lifecycle
onMounted(() => {
  // Фокус на поле текущего пароля
  const currentPasswordInput = document.getElementById("currentPassword");
  if (currentPasswordInput) {
    currentPasswordInput.focus();
  }
});
</script>

<style scoped>
.change-password-form {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.change-password-form__container {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
}

.change-password-form__title {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
  font-size: 1.75rem;
  font-weight: 600;
}

.change-password-form__error {
  margin-bottom: 1.5rem;
}

.change-password-form__success {
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

.success-message {
  display: flex;
  align-items: center;
  padding: 1rem;
  background-color: #efe;
  border: 1px solid #cfc;
  border-radius: 8px;
  color: #363;
}

.error-message__icon,
.success-message__icon {
  margin-right: 0.5rem;
  font-size: 1.1rem;
}

.error-message__text,
.success-message__text {
  flex: 1;
}

.change-password-form__form {
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

.change-password-form__submit {
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

.change-password-form__submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.change-password-form__submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.change-password-form__loading {
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

.change-password-form__actions {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}

.change-password-form__link {
  color: #667eea;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.change-password-form__link:hover {
  color: #764ba2;
  text-decoration: underline;
}

.change-password-form__link--button {
  font-size: 0.85rem;
  color: #764ba2;
}

/* Адаптивность */
@media (max-width: 480px) {
  .change-password-form {
    padding: 1rem;
  }

  .change-password-form__container {
    padding: 2rem 1.5rem;
  }

  .change-password-form__title {
    font-size: 1.5rem;
  }

  .change-password-form__actions {
    font-size: 0.8rem;
  }
}
</style>