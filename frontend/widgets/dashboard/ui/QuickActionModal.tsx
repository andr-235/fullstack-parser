"use client";

import { useState } from "react";

interface QuickActionModalProps {
  isOpen: boolean;
  onClose: () => void;
  action: string;
}

interface ActionFormData {
  groupId?: string;
  groupName?: string;
  keywords?: string;
  parserType?: string;
}

interface TextField {
  name: string;
  label: string;
  type: "text" | "textarea";
  placeholder: string;
  required: boolean;
}

interface SelectField {
  name: string;
  label: string;
  type: "select";
  options: string[];
  required: boolean;
  placeholder?: string;
}

type FieldConfig = TextField | SelectField;

const actionConfigs: Record<string, {
  title: string;
  fields: FieldConfig[];
  endpoint: string;
  method: string;
}> = {
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
};

export const QuickActionModal = ({ isOpen, onClose, action }: QuickActionModalProps) => {
  const [formData, setFormData] = useState<ActionFormData>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const config = actionConfigs[action as keyof typeof actionConfigs];

  if (!isOpen || !config) return null;

  const renderField = (field: FieldConfig) => {
    const commonProps = {
      value: formData[field.name as keyof ActionFormData] || "",
      onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => 
        handleInputChange(field.name, e.target.value),
      required: field.required,
      disabled: loading,
      className: "w-full p-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/40 focus:border-white/30 focus:outline-none disabled:opacity-50"
    };

    const fieldComponents = {
      textarea: (
        <textarea
          {...commonProps}
          placeholder={field.type === "textarea" ? field.placeholder : ""}
          rows={3}
        />
      ),
      select: (
        <select {...commonProps}>
          <option value="" className="bg-gray-800">Выберите тип</option>
          {field.type === "select" && field.options.map((option) => (
            <option key={option} value={option} className="bg-gray-800">
              {option}
            </option>
          ))}
        </select>
      ),
      text: (
        <input
          type="text"
          {...commonProps}
          placeholder={field.type === "text" ? field.placeholder : ""}
        />
      )
    };

    return (
      <div key={field.name}>
        <label className="block text-white/80 text-sm mb-2">
          {field.label}
          {field.required && <span className="text-red-400 ml-1">*</span>}
        </label>
        {fieldComponents[field.type]}
      </div>
    );
  };

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
        headers: {
          "Content-Type": "application/json",
        },
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
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 p-6 w-full max-w-md">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-white">{config.title}</h3>
          <button
            onClick={handleClose}
            disabled={loading}
            className="text-white/60 hover:text-white transition-colors disabled:opacity-50"
          >
            ✕
          </button>
        </div>

        {success ? (
          <div className="text-center py-8">
            <div className="text-green-400 text-4xl mb-4">✅</div>
            <p className="text-white text-lg">Успешно выполнено!</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {config.fields.length > 0 ? (
              config.fields.map(renderField)
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
              <button
                type="button"
                onClick={handleClose}
                disabled={loading}
                className="flex-1 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-colors disabled:opacity-50"
              >
                Отмена
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-4 py-2 rounded-lg bg-blue-500 hover:bg-blue-600 text-white transition-colors disabled:opacity-50 flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Выполняется...
                  </>
                ) : (
                  "Выполнить"
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
