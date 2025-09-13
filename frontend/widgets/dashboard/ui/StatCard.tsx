"use client";

interface StatCardProps {
  title: string;
  value: number;
  growth: number;
  icon: string;
  color: string;
  loading: boolean;
}

const COLOR_CLASSES = {
  'bg-blue-500': 'bg-blue-500/20 text-blue-400',
  'bg-green-500': 'bg-green-500/20 text-green-400',
  'bg-purple-500': 'bg-purple-500/20 text-purple-400',
  'bg-orange-500': 'bg-orange-500/20 text-orange-400',
  'bg-red-500': 'bg-red-500/20 text-red-400',
  'bg-yellow-500': 'bg-yellow-500/20 text-yellow-400',
  'bg-cyan-500': 'bg-cyan-500/20 text-cyan-400',
  'bg-indigo-500': 'bg-indigo-500/20 text-indigo-400',
} as const;

export const StatCard = ({ 
  title, 
  value, 
  growth, 
  icon, 
  color,
  loading
}: StatCardProps) => {
  const colorClasses = COLOR_CLASSES[color as keyof typeof COLOR_CLASSES] || 'bg-gray-500/20 text-gray-400';
  const isPositive = growth >= 0;

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-3 rounded-xl ${colorClasses}`}>
            <span className="text-2xl">{icon}</span>
          </div>
          <h3 className="text-sm font-medium text-white/80">{title}</h3>
        </div>
        <div className={`text-xs px-3 py-1 rounded-full font-semibold ${
          isPositive 
            ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
            : 'bg-red-500/20 text-red-400 border border-red-500/30'
        }`}>
          {isPositive ? '+' : ''}{growth}%
        </div>
      </div>
      
      <div className="space-y-2">
        <div className="text-3xl font-bold text-white">
          {loading ? (
            <div className="h-8 w-20 bg-white/20 rounded animate-pulse" />
          ) : (
            value.toLocaleString()
          )}
        </div>
        <p className="text-xs text-white/60">
          {isPositive ? 'рост' : 'снижение'} с прошлого месяца
        </p>
      </div>
    </div>
  );
};