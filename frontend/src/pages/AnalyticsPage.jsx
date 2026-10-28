import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend
} from 'recharts';
import { BarChart3, TrendingUp, AlertTriangle, ShieldCheck, RefreshCw } from 'lucide-react';
import api from '../api/client';

export const AnalyticsPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/analytics/summary?days=${days}`);
      setData(res.data);
    } catch (err) {
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [days]);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const channelData = data?.channel_breakdown || [];
  const merchantData = data?.merchant_risk || [];
  const volumeData = data?.daily_volume || [];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Macro Risk & Trend Intelligence</h1>
          <p className="text-xs text-slate-400 mt-0.5">Aggregated exposure across settlement channels and merchant tiers</p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-3 py-2 bg-[#0e162f] border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none"
          >
            <option value={7}>Past 7 Days</option>
            <option value={14}>Past 14 Days</option>
            <option value={30}>Past 30 Days</option>
            <option value={60}>Past 60 Days</option>
          </select>

          <button
            onClick={fetchAnalytics}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
          >
            <RefreshCw size={15} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Channel Risk Distribution */}
        <div className="p-5 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg">
          <h3 className="text-sm font-semibold text-white mb-1">Channel Exposure & Fraud Rate (%)</h3>
          <p className="text-[11px] text-slate-400 mb-4">Risk concentration across UPI, Mobile App, Net Banking, and POS</p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={channelData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <XAxis dataKey="channel" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090f20', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="total" name="Total Volume" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="fraud_count" name="Fraud Flagged" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Merchant Category Risk */}
        <div className="p-5 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg">
          <h3 className="text-sm font-semibold text-white mb-1">Merchant Category Risk Breakdown</h3>
          <p className="text-[11px] text-slate-400 mb-4">Incident incidence vs legitimate transaction distribution</p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={merchantData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <XAxis dataKey="category" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090f20', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="fraud_rate" name="Fraud Rate %" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
