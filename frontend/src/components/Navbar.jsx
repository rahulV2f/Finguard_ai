import React from 'react';
import { ShieldCheck, Bell, Activity, Sparkles, RefreshCw } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Navbar = ({ onQuickGenerate }) => {
  const { user } = useAuth();

  return (
    <header className="h-16 px-6 bg-[#0e162f]/80 backdrop-blur-md border-b border-slate-800 flex items-center justify-between sticky top-0 z-20">
      {/* Left: Security Status Badge */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-950/60 border border-emerald-800/60 text-emerald-400 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          AI Model: Active Ensemble (v1.0.0)
        </div>
        <div className="hidden md:flex items-center gap-1.5 text-xs text-slate-400">
          <Activity size={14} className="text-cyan-400" />
          <span>Latency: 4.8ms</span>
        </div>
      </div>

      {/* Right: Quick Action & Profile */}
      <div className="flex items-center gap-3">
        {onQuickGenerate && (
          <button
            onClick={onQuickGenerate}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold rounded-lg shadow-md transition-all active:scale-95"
          >
            <Sparkles size={14} />
            <span>Simulate Traffic</span>
          </button>
        )}

        <div className="h-6 w-px bg-slate-800 mx-1"></div>

        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
            {user?.role}
          </span>
          <span className="text-xs text-slate-300 font-medium hidden sm:inline">
            {user?.full_name}
          </span>
        </div>
      </div>
    </header>
  );
};
