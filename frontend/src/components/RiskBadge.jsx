import React from 'react';

export const RiskBadge = ({ category, score }) => {
  let bg = 'bg-slate-800 text-slate-300 border-slate-700';
  let dot = 'bg-slate-400';

  if (category === 'CRITICAL' || score >= 80) {
    bg = 'bg-rose-950/70 text-rose-300 border-rose-800/80';
    dot = 'bg-rose-500 animate-pulse';
  } else if (category === 'HIGH' || score >= 60) {
    bg = 'bg-orange-950/70 text-orange-300 border-orange-800/80';
    dot = 'bg-orange-500';
  } else if (category === 'MEDIUM' || score >= 30) {
    bg = 'bg-amber-950/70 text-amber-300 border-amber-800/80';
    dot = 'bg-amber-500';
  } else {
    bg = 'bg-emerald-950/70 text-emerald-300 border-emerald-800/80';
    dot = 'bg-emerald-500';
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${bg}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dot}`}></span>
      {category || 'LOW'} {score !== undefined ? `(${score})` : ''}
    </span>
  );
};
