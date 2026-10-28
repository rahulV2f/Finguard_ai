import React, { useState, useEffect } from 'react';
import {
  Briefcase, MessageSquare, CheckCircle2, AlertTriangle, ShieldCheck,
  ChevronLeft, ChevronRight, RefreshCw, Send, User, Clock
} from 'lucide-react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

export const CasesPage = () => {
  const [cases, setCases] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [selectedCase, setSelectedCase] = useState(null);
  const [newNote, setNewNote] = useState('');
  const [postingNote, setPostingNote] = useState(false);
  const { user } = useAuth();

  const fetchCases = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/cases/?page=${page}&page_size=15`);
      setCases(res.data.items);
      setTotal(res.data.total);
      if (selectedCase) {
        // Refresh selected case details
        const updated = res.data.items.find(c => c.id === selectedCase.id);
        if (updated) setSelectedCase(updated);
      }
    } catch (err) {
      console.error('Error fetching cases:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [page]);

  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!newNote.trim() || !selectedCase) return;
    setPostingNote(true);
    try {
      await api.post(`/cases/${selectedCase.id}/notes`, { note: newNote });
      setNewNote('');
      // Re-fetch case detail
      const res = await api.get(`/cases/${selectedCase.id}`);
      setSelectedCase(res.data);
      fetchCases();
    } catch (err) {
      alert('Failed to post note');
    } finally {
      setPostingNote(false);
    }
  };

  const handleUpdateCaseStatus = async (status, outcome) => {
    if (!selectedCase) return;
    try {
      await api.patch(`/cases/${selectedCase.id}`, { status, outcome });
      const res = await api.get(`/cases/${selectedCase.id}`);
      setSelectedCase(res.data);
      fetchCases();
    } catch (err) {
      alert('Failed to update case');
    }
  };

  const getStatusBadge = (st) => {
    switch (st) {
      case 'OPEN':
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-blue-950 text-blue-300 border border-blue-800">OPEN</span>;
      case 'INVESTIGATING':
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-950 text-amber-300 border border-amber-800">INVESTIGATING</span>;
      case 'ESCALATED':
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-purple-950 text-purple-300 border border-purple-800">ESCALATED</span>;
      case 'CLOSED_FRAUD':
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-950 text-rose-300 border border-rose-800">CLOSED (FRAUD)</span>;
      case 'CLOSED_LEGITIMATE':
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-800">CLOSED (LEGIT)</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-800 text-slate-300">{st}</span>;
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <span>Fraud Investigation Case Files</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Audit-tracked investigative workflows, analyst notes, and documented resolution evidence
          </p>
        </div>

        <button
          onClick={fetchCases}
          className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 self-start md:self-auto"
        >
          <RefreshCw size={15} />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cases List */}
        <div className="lg:col-span-1 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg overflow-hidden flex flex-col h-[700px]">
          <div className="p-3.5 bg-[#090f20] border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Active Case Roster ({cases.length})
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-slate-800/60 p-2">
            {loading ? (
              <div className="p-8 text-center text-slate-500 text-xs">Loading cases...</div>
            ) : cases.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">No active cases opened yet.</div>
            ) : (
              cases.map((c) => (
                <div
                  key={c.id}
                  onClick={() => setSelectedCase(c)}
                  className={`p-3 rounded-xl cursor-pointer transition-colors ${
                    selectedCase?.id === c.id ? 'bg-blue-600/20 border border-blue-500/50' : 'hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono text-xs font-bold text-white">{c.case_ref}</span>
                    {getStatusBadge(c.status)}
                  </div>
                  <p className="text-xs text-slate-300 line-clamp-1 font-medium">{c.title}</p>
                  <div className="flex items-center justify-between mt-2 text-[11px] text-slate-400">
                    <span>Priority: {c.priority}</span>
                    <span>{new Date(c.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Selected Case Workspace */}
        <div className="lg:col-span-2 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg flex flex-col h-[700px]">
          {selectedCase ? (
            <div className="flex flex-col h-full">
              {/* Header */}
              <div className="p-4 border-b border-slate-800 bg-[#090f20] flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm font-bold text-cyan-400">{selectedCase.case_ref}</span>
                    {getStatusBadge(selectedCase.status)}
                  </div>
                  <h3 className="text-sm font-semibold text-white mt-0.5">{selectedCase.title}</h3>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleUpdateCaseStatus('CLOSED_FRAUD', 'FRAUD_CONFIRMED')}
                    className="px-2.5 py-1 rounded-lg bg-rose-950/80 hover:bg-rose-900 border border-rose-800 text-rose-300 text-xs font-semibold"
                  >
                    Close as Fraud
                  </button>
                  <button
                    onClick={() => handleUpdateCaseStatus('CLOSED_LEGITIMATE', 'FALSE_POSITIVE')}
                    className="px-2.5 py-1 rounded-lg bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-800 text-emerald-300 text-xs font-semibold"
                  >
                    Close as Legit
                  </button>
                </div>
              </div>

              {/* Case Details Summary */}
              <div className="p-3 bg-slate-900/60 border-b border-slate-800 grid grid-cols-3 gap-2 text-xs">
                <div>
                  <span className="text-slate-500 block">Lead Investigator</span>
                  <span className="font-semibold text-slate-200">{selectedCase.assignee?.full_name || 'Unassigned'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Investigation Outcome</span>
                  <span className="font-bold text-amber-400">{selectedCase.outcome}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Opened Date</span>
                  <span className="text-slate-300">{new Date(selectedCase.created_at).toLocaleString()}</span>
                </div>
              </div>

              {/* Analyst Notes Timeline */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Investigative Audit Trail & Analyst Notes:
                </p>

                {(!selectedCase.notes || selectedCase.notes.length === 0) ? (
                  <div className="py-8 text-center text-slate-500 text-xs">
                    No notes recorded yet. Add initial investigative findings below.
                  </div>
                ) : (
                  selectedCase.notes.map((n) => (
                    <div key={n.id} className="p-3 rounded-xl bg-[#090f20] border border-slate-800 text-xs space-y-1">
                      <div className="flex items-center justify-between text-slate-400">
                        <span className="font-semibold text-cyan-400 flex items-center gap-1">
                          <User size={12} />
                          {n.author_name}
                        </span>
                        <span className="text-[10px] flex items-center gap-1">
                          <Clock size={10} />
                          {new Date(n.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-slate-200 leading-relaxed text-[11px] pt-1">{n.note}</p>
                    </div>
                  ))
                )}
              </div>

              {/* Add Note Input Form */}
              <form onSubmit={handleAddNote} className="p-3 border-t border-slate-800 bg-[#090f20] flex gap-2">
                <input
                  type="text"
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Record an investigation update, cardholder response, or KYC check..."
                  className="flex-1 px-3 py-2 bg-[#0e162f] border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
                <button
                  type="submit"
                  disabled={postingNote || !newNote.trim()}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors"
                >
                  <Send size={14} />
                  <span>Log</span>
                </button>
              </form>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center p-8 text-center text-slate-500 text-xs">
              Select an investigation case from the roster to inspect findings and append notes.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
