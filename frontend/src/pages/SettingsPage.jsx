import React, { useState } from 'react';
import { Settings, Shield, Sliders, Database, Key, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const SettingsPage = () => {
  const { user, isAdmin } = useAuth();
  const [lowMax, setLowMax] = useState(29);
  const [medMax, setMedMax] = useState(59);
  const [highMax, setHighMax] = useState(79);
  const [alertTrigger, setAlertTrigger] = useState(60);
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <span>System & Risk Governance Settings</span>
        </h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Configure risk score boundaries, automated escalation thresholds, and runtime security policies
        </p>
      </div>

      {saved && (
        <div className="p-3 rounded-xl bg-emerald-950/70 border border-emerald-800 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 size={16} />
          <span>Risk thresholds updated in memory successfully.</span>
        </div>
      )}

      {/* Threshold Configuration */}
      <form onSubmit={handleSave} className="p-6 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg space-y-6">
        <h3 className="text-sm font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
          <Sliders size={16} className="text-cyan-400" />
          <span>Configurable Risk Score Bands (0 - 100)</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div>
            <label className="block text-emerald-400 font-semibold mb-1">Low Risk Maximum</label>
            <input
              type="number"
              min="10"
              max="40"
              value={lowMax}
              onChange={(e) => setLowMax(Number(e.target.value))}
              className="w-full px-3 py-2 bg-[#090f20] border border-slate-700 rounded-xl text-white font-mono"
            />
            <span className="text-[10px] text-slate-500 mt-1 block">Scores 0 - {lowMax} treated as Low risk</span>
          </div>

          <div>
            <label className="block text-amber-400 font-semibold mb-1">Medium Risk Maximum</label>
            <input
              type="number"
              min="40"
              max="70"
              value={medMax}
              onChange={(e) => setMedMax(Number(e.target.value))}
              className="w-full px-3 py-2 bg-[#090f20] border border-slate-700 rounded-xl text-white font-mono"
            />
            <span className="text-[10px] text-slate-500 mt-1 block">Scores {lowMax + 1} - {medMax} treated as Medium</span>
          </div>

          <div>
            <label className="block text-rose-400 font-semibold mb-1">High Risk Maximum</label>
            <input
              type="number"
              min="70"
              max="90"
              value={highMax}
              onChange={(e) => setHighMax(Number(e.target.value))}
              className="w-full px-3 py-2 bg-[#090f20] border border-slate-700 rounded-xl text-white font-mono"
            />
            <span className="text-[10px] text-slate-500 mt-1 block">Scores {medMax + 1} - {highMax} treated as High; {highMax + 1}+ is Critical</span>
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">
            Automated Alert Dispatch Threshold: <span className="text-cyan-400 font-bold">{alertTrigger}</span>
          </label>
          <input
            type="range"
            min="40"
            max="80"
            value={alertTrigger}
            onChange={(e) => setAlertTrigger(Number(e.target.value))}
            className="w-full accent-blue-500 cursor-pointer"
          />
          <span className="text-[10px] text-slate-500">Any incoming transaction scoring {alertTrigger} or higher will instantly spawn a triage Alert.</span>
        </div>

        <div className="flex justify-end pt-3 border-t border-slate-800">
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs rounded-xl shadow-md transition-colors"
          >
            Apply Risk Thresholds
          </button>
        </div>
      </form>

      {/* Security Architecture & Simulation Notice */}
      <div className="p-6 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg space-y-3 text-xs">
        <h3 className="text-sm font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
          <Shield size={16} className="text-emerald-400" />
          <span>Platform Disclaimer & Educational Notice</span>
        </h3>
        <p className="text-slate-300 leading-relaxed text-[11px]">
          <strong>FinGuard AI</strong> is an engineering prototype designed strictly for simulated banking transaction analysis,
          machine learning risk scoring, and interactive fraud investigation. It operates entirely on synthetic data,
          connects to no real payment networks, does not hold live funds, and does not claim official affiliation with any commercial bank.
        </p>
        <div className="p-3 rounded-xl bg-[#090f20] border border-slate-800 text-[11px] text-slate-400 space-y-1">
          <div><strong className="text-slate-300">Backend Engine:</strong> Python 3.13, FastAPI, SQLAlchemy ORM, SQLite / PostgreSQL</div>
          <div><strong className="text-slate-300">ML Pipeline:</strong> scikit-learn Balanced Random Forest, PR-AUC Calibration, SHAP-Style Factor Attribution</div>
          <div><strong className="text-slate-300">Frontend Stack:</strong> React 19, Vite, Tailwind CSS, Recharts, Lucide Icons</div>
        </div>
      </div>
    </div>
  );
};
