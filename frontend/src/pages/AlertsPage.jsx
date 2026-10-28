import React, { useState, useEffect } from 'react';
import {
  Bell, AlertTriangle, ShieldCheck, CheckCircle2, ChevronLeft, ChevronRight,
  UserCheck, ExternalLink, RefreshCw, Briefcase
} from 'lucide-react';
import api from '../api/client';
import { RiskBadge } from '../components/RiskBadge';

export const AlertsPage = () => {
  const [alerts, setAlerts] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [actionNotes, setActionNotes] = useState('');

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      let url = `/alerts/?page=${page}&page_size=15`;
      if (statusFilter) url += `&status=${statusFilter}`;
      const res = await api.get(url);
      setAlerts(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      console.error('Error fetching alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [page, statusFilter]);

  const handleUpdateStatus = async (newStatus) => {
    if (!selectedAlert) return;
    try {
      await api.patch(`/alerts/${selectedAlert.id}`, {
        status: newStatus,
        notes: actionNotes
      });
      setSelectedAlert(null);
      setActionNotes('');
      fetchAlerts();
    } catch (err) {
      alert('Failed to update alert');
    }
  };

  const handleOpenCase = async () => {
    if (!selectedAlert) return;
    try {
      await api.post('/cases/', {
        alert_id: selectedAlert.id,
        title: `Investigation: Alert ${selectedAlert.alert_ref} (Score: ${selectedAlert.risk_score})`
      });
      alert('Investigation Case opened successfully! Redirecting...');
      window.location.href = '/cases';
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to open case');
    }
  };

  const getStatusBadge = (st) => {
    switch (st) {
      case 'NEW':
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-blue-950 text-blue-300 border border-blue-800">NEW</span>;
      case 'UNDER_REVIEW':
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-950 text-amber-300 border border-amber-800">UNDER REVIEW</span>;
      case 'ESCALATED':
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-purple-950 text-purple-300 border border-purple-800">ESCALATED</span>;
      case 'CONFIRMED_FRAUD':
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-950 text-rose-300 border border-rose-800">CONFIRMED FRAUD</span>;
      case 'FALSE_POSITIVE':
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-800">FALSE POSITIVE</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-800 text-slate-300 border border-slate-700">{st}</span>;
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <span>Fraud Alerts Surveillance Queue</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time compliance triage for transactions exceeding safety thresholds
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className="px-3 py-2 bg-[#0e162f] border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Alert Statuses</option>
            <option value="NEW">New</option>
            <option value="UNDER_REVIEW">Under Review</option>
            <option value="ESCALATED">Escalated</option>
            <option value="CONFIRMED_FRAUD">Confirmed Fraud</option>
            <option value="FALSE_POSITIVE">False Positive</option>
          </select>

          <button
            onClick={fetchAlerts}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
          >
            <RefreshCw size={15} />
          </button>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#090f20] border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Alert Ref</th>
                <th className="py-3 px-4">Creation Time</th>
                <th className="py-3 px-4">Risk Severity</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Detection Model</th>
                <th className="py-3 px-4 text-right">Triage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                    Loading alert queue...
                  </td>
                </tr>
              ) : alerts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    No alerts match the chosen filters.
                  </td>
                </tr>
              ) : (
                alerts.map((a) => (
                  <tr key={a.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-semibold text-white">{a.alert_ref}</td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {new Date(a.created_at).toLocaleDateString()} {new Date(a.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-3.5 px-4">
                      <RiskBadge category={a.risk_category} score={a.risk_score} />
                    </td>
                    <td className="py-3.5 px-4">{getStatusBadge(a.status)}</td>
                    <td className="py-3.5 px-4">
                      <span className="font-semibold text-slate-300">{a.priority}</span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">{a.detection_method}</td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => setSelectedAlert(a)}
                        className="px-3 py-1 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold transition-colors shadow-sm"
                      >
                        Investigate
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="p-4 bg-[#090f20] border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span>Showing page {page} of {Math.max(1, Math.ceil(total / 15))} ({total} total alerts)</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page <= 1}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300"
            >
              <ChevronLeft size={16} />
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={page * 15 >= total}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Alert Investigation Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0e162f] border border-slate-800 rounded-2xl max-w-xl w-full p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <span>Alert Decisioning Desk</span>
                </h3>
                <p className="text-xs text-slate-400 font-mono">{selectedAlert.alert_ref}</p>
              </div>
              <RiskBadge category={selectedAlert.risk_category} score={selectedAlert.risk_score} />
            </div>

            <div className="space-y-4 text-xs">
              <div className="p-3 rounded-xl bg-[#090f20] border border-slate-800 grid grid-cols-2 gap-2">
                <div>
                  <span className="text-slate-500 block">Current Status</span>
                  <div className="mt-1">{getStatusBadge(selectedAlert.status)}</div>
                </div>
                <div>
                  <span className="text-slate-500 block">Priority Level</span>
                  <span className="font-bold text-amber-400">{selectedAlert.priority}</span>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Analyst Decision Rationale / Notes</label>
                <textarea
                  rows={2}
                  value={actionNotes}
                  onChange={(e) => setActionNotes(e.target.value)}
                  placeholder="Record justification, customer verification confirmation, or false positive reason..."
                  className="w-full p-2.5 bg-[#090f20] border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              {/* Action Buttons */}
              <div className="pt-2 border-t border-slate-800 space-y-2">
                <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Execute Resolution Decision:</p>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  <button
                    onClick={() => handleUpdateStatus('CONFIRMED_FRAUD')}
                    className="py-2 px-3 rounded-xl bg-rose-950/80 hover:bg-rose-900 border border-rose-800 text-rose-200 font-semibold text-xs"
                  >
                    Confirm Fraud
                  </button>
                  <button
                    onClick={() => handleUpdateStatus('FALSE_POSITIVE')}
                    className="py-2 px-3 rounded-xl bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-800 text-emerald-200 font-semibold text-xs"
                  >
                    Mark False Positive
                  </button>
                  <button
                    onClick={() => handleUpdateStatus('ESCALATED')}
                    className="py-2 px-3 rounded-xl bg-purple-950/80 hover:bg-purple-900 border border-purple-800 text-purple-200 font-semibold text-xs"
                  >
                    Escalate to L2
                  </button>
                </div>

                <div className="pt-2">
                  <button
                    onClick={handleOpenCase}
                    className="w-full py-2.5 px-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center justify-center gap-1.5 shadow-md"
                  >
                    <Briefcase size={14} />
                    <span>Open Formal Investigation Case</span>
                  </button>
                </div>
              </div>
            </div>

            <div className="mt-4 flex justify-end">
              <button
                onClick={() => setSelectedAlert(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
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
