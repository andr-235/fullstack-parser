"use client";

import { useState } from "react";
import { CustomModal } from "./CustomModal";
import { Input } from "./CustomInput";
import { Textarea } from "./CustomTextarea";
import { Button } from "./CustomButton";

interface QuickActionModalProps {
  isOpen: boolean;
  onClose: () => void;
  action: string;
}

interface FormData {
  groupId?: string;
  groupName?: string;
  keywords?: string;
}

const ACTION_CONFIGS = {
  "Добавить новую группу": {
    title: "Добавить новую группу",
    fields: [
      { name: "groupId", label: "ID группы", type: "text", placeholder: "123456789", required: true },
      { name: "groupName", label: "Название группы", type: "text", placeholder: "Название группы", required: true }
    ],
    endpoint: "/api/v1/groups/",
    method: "POST"
  },
  "Настроить ключевые слова": {
    title: "Настроить ключевые слова",
    fields: [
      { name: "keywords", label: "Ключевые слова", type: "textarea", placeholder: "Введите ключевые слова через запятую", required: true }
    ],
    endpoint: "/api/v1/keywords/",
    method: "POST"
  },
  "Запустить парсер": {
    title: "Запустить парсер комментариев",
    fields: [],
    endpoint: "/api/v1/parser/start",
    method: "POST"
  }
} as const;

export const QuickActionModal = ({ isOpen, onClose, action }: QuickActionModalProps) => {
  const [formData, setFormData] = useState<FormData>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const config = ACTION_CONFIGS[action as keyof typeof ACTION_CONFIGS];

  if (!isOpen || !config) return null;

  const handleInputChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(config.endpoint, {
        method: config.method,
        headers: { "Content-Type": "application/json" },
        body: config.fields.length > 0 ? JSON.stringify(formData) : JSON.stringify({}),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Ошибка выполнения запроса");
      }

      setSuccess(true);
      setTimeout(() => {
        onClose();
        setSuccess(false);
        setFormData({});
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Произошла ошибка");
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
      setFormData({});
      setError(null);
      setSuccess(false);
    }
  };

  return (
    <CustomModal isOpen={isOpen} onClose={handleClose} title={config.title}>
      {success ? (
        <div className="text-center py-8">
          <div className="text-green-400 text-4xl mb-4">✅</div>
          <p className="text-white text-lg">Успешно выполнено!</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          {config.fields.length > 0 ? (
            config.fields.map((field) => {
              const commonProps = {
                value: formData[field.name as keyof FormData] || "",
                onChange: (value: string) => handleInputChange(field.name, value),
                required: field.required,
                disabled: loading,
                label: field.label,
                placeholder: field.placeholder || ""
              };

              return field.type === "textarea" ? (
                <Textarea key={field.name} {...commonProps} rows={3} />
              ) : (
                <Input key={field.name} {...commonProps} type="text" />
              );
            })
          ) : (
            <div className="text-center py-4">
              <p className="text-white/80 mb-4">
                Запустить парсер комментариев для всех активных групп?
              </p>
            </div>
          )}

          {error && (
            <div className="p-3 rounded-lg bg-red-500/20 border border-red-500/30 text-red-400 text-sm">
              {error}
            </div>
          )}

          <div className="flex space-x-3 pt-4">
            <Button
              type="button"
              onClick={handleClose}
              disabled={loading}
              variant="ghost"
              className="flex-1"
            >
              Отмена
            </Button>
            <Button
              type="submit"
              disabled={loading}
              loading={loading}
              className="flex-1"
            >
              Выполнить
            </Button>
          </div>
        </form>
      )}
    </CustomModal>
  );
};