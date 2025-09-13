"use client";

interface StatCardProps {
  title: string;
  value: number;
  growth: number;
  icon: string;
  color: string;
  loading: boolean;
}

export const StatCard = ({ 
  title, 
  value, 
  growth, 
  icon, 
  color,
  loading
}: StatCardProps) => (
  <div className="group relative overflow-hidden rounded-xl bg-white/5 border border-white/10 p-6 transition-all duration-300 hover:bg-white/10 hover:scale-105">
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center space-x-3">
        <div className={`p-3 rounded-xl ${color} bg-opacity-20`}>
          <span className="text-2xl">{icon}</span>
        </div>
        <h3 className="text-sm font-medium text-white/80">{title}</h3>
      </div>
      <div className={`text-xs px-2 py-1 rounded-full ${
        growth >= 0 
          ? 'bg-green-500/20 text-green-400' 
          : 'bg-red-500/20 text-red-400'
      }`}>
        {growth >= 0 ? '+' : ''}{growth}%
      </div>
    </div>
    
    <div className="space-y-1">
      <div className="text-3xl font-bold text-white">
        {loading ? (
          <div className="h-8 w-20 bg-white/20 rounded animate-pulse" />
        ) : (
          value.toLocaleString()
        )}
      </div>
      <p className="text-xs text-white/60">
        {growth >= 0 ? 'рост' : 'снижение'} с прошлого месяца
      </p>
    </div>
  </div>
);
