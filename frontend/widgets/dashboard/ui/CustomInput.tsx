"use client";

interface InputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  type?: "text" | "email" | "password" | "number";
  className?: string;
  label?: string;
  required?: boolean;
  error?: string;
}

export const Input = ({
  value,
  onChange,
  placeholder,
  disabled = false,
  type = "text",
  className = "",
  label,
  required = false,
  error
}: InputProps) => {
  const inputClasses = `
    w-full px-4 py-3 rounded-lg border transition-all duration-200
    bg-white/5 border-white/20 text-white placeholder-white/40
    focus:border-white/40 focus:outline-none focus:ring-2 focus:ring-white/20
    disabled:opacity-50 disabled:cursor-not-allowed
    ${error ? 'border-red-400 focus:border-red-400 focus:ring-red-400/20' : ''}
    ${className}
  `.trim();

  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-white/80">
          {label}
          {required && <span className="text-red-400 ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        className={inputClasses}
      />
      {error && (
        <p className="text-sm text-red-400">{error}</p>
      )}
    </div>
  );
};

// Обратная совместимость
export const CustomInput = Input;
