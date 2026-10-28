import React, { useState, useEffect } from 'react';
import {
  ShieldAlert, Activity, AlertTriangle, ArrowUpRight, CheckCircle2,
  TrendingUp, CreditCard, RefreshCw, Eye, Sparkles
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import api from '../api/client';
import { RiskBadge } from '../components/RiskBadge';

export const DashboardPage = () => {
  const [data, setData] = useState(null);
  const [recentTxns, setRecentTxns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [selectedTxn, setSelectedTxn] = useState(null);

  const fetchDashboardData = async () => {
    try {
      const [analyticsRes, txnsRes] = await Promise.all([
        api.get('/analytics/summary?days=14'),
        api.get('/transactions/?page=1&page_size=8&is_flagged=true')
      ]);
      setData(analyticsRes.data);
      setRecentTxns(txnsRes.data.items);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleSimulateBurst = async () => {
    setSimulating(true);
    try {
      await api.post('/transactions/generate-synthetic', { count: 15, fraud_ratio: 0.35 });
      await fetchDashboardData();
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setSimulating(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm text-slate-400">Loading banking risk intelligence...</p>
        </div>
      </div>
    );
  }

  const stats = data?.stats || {};
  const dailyVolume = data?.daily_volume || [];
  const riskDist = data?.risk_distribution || [];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Banner / Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            Banking Risk Intelligence Center
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time transaction surveillance, ML risk scoring, and automated compliance alerts
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchDashboardData}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
            title="Refresh analytics"
          >
            <RefreshCw size={16} />
          </button>
          <button
            onClick={handleSimulateBurst}
            disabled={simulating}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-blue-600/30 transition-all active:scale-95 disabled:opacity-50"
          >
            <Sparkles size={15} />
            <span>{simulating ? 'Injecting Transactions...' : 'Simulate Live Transactions'}</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Transactions */}
        <div className="p-5 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Surveillance</span>
            <div className="w-8 h-8 rounded-lg bg-blue-950/60 border border-blue-800/60 flex items-center justify-center text-blue-400">
              <CreditCard size={18} />
            </div>
          </div>
          <div className="text-2xl font-bold text-white">{stats.total_transactions?.toLocaleString() || 0}</div>
          <p className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1 font-medium">
            <TrendingUp size={12} />
            <span>100% processed via Hybrid ML</span>
          </p>
        </div>

        {/* Flagged Transactions */}
        <div className="p-5 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Flagged Suspicious</span>
            <div className="w-8 h-8 rounded-lg bg-amber-950/60 border border-amber-800/60 flex items-center justify-center text-amber-400">
              <AlertTriangle size={18} />
            </div>
          </div>
          <div className="text-2xl font-bold text-amber-400">{stats.flagged_transactions || 0}</div>
          <p className="text-[11px] text-slate-400 mt-1">
            Simulated Fraud Rate: <span className="font-semibold text-slate-200">{stats.fraud_rate_pct}%</span>
          </p>
        </div>

        {/* High / Critical Alerts */}
        <div className="p-5 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">High Risk Alerts</span>
            <div className="w-8 h-8 rounded-lg bg-rose-950/60 border border-rose-800/60 flex items-center justify-center text-rose-400">
              <ShieldAlert size={18} />
            </div>
          </div>
          <div className="text-2xl font-bold text-rose-400">{stats.high_risk_transactions || 0}</div>
          <p className="text-[11px] text-slate-400 mt-1">
            Pending Analyst Triage: <span className="font-semibold text-rose-300">{stats.pending_alerts || 0}</span>
          </p>
        </div>

        {/* Fraud Loss Prevented */}
        <div className="p-5 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Loss Prevented</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-950/60 border border-emerald-800/60 flex items-center justify-center text-emerald-400">
              <CheckCircle2 size={18} />
            </div>
          </div>
          <div className="text-2xl font-bold text-emerald-400">
            ₹{stats.total_fraud_loss_prevented?.toLocaleString() || '0.00'}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Model Offline Accuracy: <span className="font-semibold text-emerald-300">{stats.model_accuracy_pct}%</span>
          </p>
        </div>
      </div>

      {/* Charts Section: Volume Trend & Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Daily Volume & Anomaly Trend */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-white">Daily Transaction Flow & Anomalies</h3>
                <p className="text-[11px] text-slate-400">Legitimate vs Suspicious volume correlation over time</p>
              </div>
              <div className="flex items-center gap-3 text-xs">
                <span className="flex items-center gap-1.5 text-slate-300">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Legitimate
                </span>
                <span className="flex items-center gap-1.5 text-slate-300">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> Flagged
                </span>
              </div>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={dailyVolume} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="legitColor" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                    </linearGradient>
                    <linearGradient id="fraudColor" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.6} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#090f20', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Area type="monotone" dataKey="legitimate_count" stroke="#3b82f6" fillOpacity={1} fill="url(#legitColor)" />
                  <Area type="monotone" dataKey="fraud_count" stroke="#ef4444" fillOpacity={1} fill="url(#fraudColor)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Risk Category Distribution Donut */}
        <div className="p-5 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white mb-1">Risk Category Composition</h3>
            <p className="text-[11px] text-slate-400 mb-4">Transaction division by risk bands</p>
            <div className="h-52 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskDist}
                    dataKey="count"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={4}
                  >
                    {riskDist.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#090f20', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800 text-xs">
            {riskDist.map((item) => (
              <div key={item.category} className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-slate-300">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }}></span>
                  {item.category}
                </span>
                <span className="font-semibold text-white">{item.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Suspicious Transactions Table */}
      <div className="p-5 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Recent Flagged Transactions</h3>
            <p className="text-[11px] text-slate-400">Transactions with risk scores exceeding configured threshold</p>
          </div>
          <a href="/transactions" className="text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center gap-1">
            <span>View All Transactions</span>
            <ArrowUpRight size={14} />
          </a>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-medium">
                <th className="pb-3 pl-2">Transaction Ref</th>
                <th className="pb-3">Customer ID</th>
                <th className="pb-3">Amount</th>
                <th className="pb-3">Channel</th>
                <th className="pb-3">Category</th>
                <th className="pb-3">Risk Assessment</th>
                <th className="pb-3 pr-2 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {recentTxns.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-6 text-center text-slate-500">
                    No flagged transactions currently detected. Click "Simulate Live Transactions" to generate activity.
                  </td>
                </tr>
              ) : (
                recentTxns.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 pl-2 font-mono font-semibold text-white">{t.transaction_ref}</td>
                    <td className="py-3 font-mono text-cyan-400">{t.customer_id}</td>
                    <td className="py-3 font-semibold text-white">₹{t.amount.toLocaleString()}</td>
                    <td className="py-3 text-slate-400">{t.payment_channel}</td>
                    <td className="py-3">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                        {t.merchant_category}
                      </span>
                    </td>
                    <td className="py-3">
                      <RiskBadge category={t.risk_category} score={t.risk_score} />
                    </td>
                    <td className="py-3 pr-2 text-right">
                      <button
                        onClick={() => setSelectedTxn(t)}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                        title="Explain risk factors"
                      >
                        <Eye size={15} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Explainability Quick Modal */}
      {selectedTxn && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0e162f] border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl relative">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <div>
                <h4 className="text-base font-bold text-white flex items-center gap-2">
                  <span>Risk Intelligence Breakdown</span>
                </h4>
                <p className="text-xs text-slate-400 font-mono">{selectedTxn.transaction_ref}</p>
              </div>
              <RiskBadge category={selectedTxn.risk_category} score={selectedTxn.risk_score} />
            </div>

            <div className="space-y-3">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-slate-500">Amount:</span> <span className="font-semibold text-white">₹{selectedTxn.amount}</span>
                </div>
                <div>
                  <span className="text-slate-500">ML Confidence:</span> <span className="font-semibold text-cyan-400">{(selectedTxn.ml_probability * 100).toFixed(1)}%</span>
                </div>
                <div>
                  <span className="text-slate-500">Channel:</span> <span className="text-slate-300">{selectedTxn.payment_channel}</span>
                </div>
                <div>
                  <span className="text-slate-500">IP Risk:</span> <span className="text-slate-300">{selectedTxn.ip_risk_score}/100</span>
                </div>
              </div>

              <div>
                <h5 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Explainable AI Drivers:</h5>
                <div className="space-y-2">
                  {(() => {
                    try {
                      const reasons = JSON.parse(selectedTxn.reasons || '[]');
                      if (!reasons.length) return <p className="text-xs text-slate-500">No specific adverse risk factors triggered.</p>;
                      return reasons.map((r, i) => (
                        <div key={i} className="p-2.5 rounded-lg bg-rose-950/30 border border-rose-900/50 text-xs">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-semibold text-rose-300">{r.factor}</span>
                            <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-rose-900 text-rose-200">{r.severity}</span>
                          </div>
                          <p className="text-slate-300 text-[11px] leading-relaxed">{r.description}</p>
                        </div>
                      ));
                    } catch (e) {
                      return <p className="text-xs text-slate-400">Standard behavior.</p>;
                    }
                  })()}
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setSelectedTxn(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
