"use client";

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps {
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  label?: string;
  required?: boolean;
  error?: string;
}

export const Select = ({
  value,
  onChange,
  options,
  placeholder,
  disabled = false,
  className = "",
  label,
  required = false,
  error
}: SelectProps) => {
  const selectClasses = `
    w-full px-4 py-3 rounded-lg border transition-all duration-200
    bg-white/5 border-white/20 text-white
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
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        required={required}
        className={selectClasses}
      >
        {placeholder && (
          <option value="" className="bg-gray-800 text-white/60">
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option 
            key={option.value} 
            value={option.value}
            className="bg-gray-800 text-white"
          >
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="text-sm text-red-400">{error}</p>
      )}
    </div>
  );
};

// Обратная совместимость
export const CustomSelect = Select;
