import React, { useState, useEffect } from 'react';
import {
  Search, Filter, Download, Upload, Plus, ChevronLeft, ChevronRight,
  Eye, RefreshCw, Sparkles, FileText
} from 'lucide-react';
import api from '../api/client';
import { RiskBadge } from '../components/RiskBadge';

export const TransactionsPage = () => {
  const [transactions, setTransactions] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [channelFilter, setChannelFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedTxn, setSelectedTxn] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [showGenModal, setShowGenModal] = useState(false);
  const [genCount, setGenCount] = useState(50);
  const [genFraudRatio, setGenFraudRatio] = useState(0.15);

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      let url = `/transactions/?page=${page}&page_size=${pageSize}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      if (riskFilter) url += `&risk_category=${riskFilter}`;
      if (channelFilter) url += `&payment_channel=${channelFilter}`;

      const res = await api.get(url);
      setTransactions(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      console.error('Error fetching transactions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [page, riskFilter, channelFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchTransactions();
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    setUploading(true);
    try {
      const res = await api.post('/transactions/upload-csv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      alert(`CSV Ingestion Successful: ${res.data.imported_count} transactions imported.`);
      fetchTransactions();
    } catch (err) {
      alert(`Upload failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setUploading(false);
      e.target.value = null;
    }
  };

  const handleGenerateSynthetic = async () => {
    setShowGenModal(false);
    setLoading(true);
    try {
      await api.post('/transactions/generate-synthetic', {
        count: parseInt(genCount),
        fraud_ratio: parseFloat(genFraudRatio)
      });
      setPage(1);
      await fetchTransactions();
    } catch (err) {
      alert('Generation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Financial Transactions Ledger</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Surveillance of incoming payments, transfers, and point-of-sale executions
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Download Sample CSV */}
          <a
            href="/api/v1/transactions/sample-csv/download"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl border border-slate-700 transition-colors"
          >
            <Download size={14} />
            <span>Sample CSV</span>
          </a>

          {/* Upload CSV */}
          <label className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl border border-slate-700 cursor-pointer transition-colors">
            <Upload size={14} />
            <span>{uploading ? 'Parsing...' : 'Import CSV'}</span>
            <input type="file" accept=".csv" onChange={handleFileUpload} className="hidden" disabled={uploading} />
          </label>

          {/* Generate Synthetic Modal Trigger */}
          <button
            onClick={() => setShowGenModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold rounded-xl shadow-md transition-all active:scale-95"
          >
            <Sparkles size={14} />
            <span>Generate Traffic</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg flex flex-col md:flex-row gap-3">
        <form onSubmit={handleSearchSubmit} className="flex-1 relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by transaction reference, customer ID, or merchant..."
            className="w-full pl-9 pr-3 py-2 bg-[#090f20] border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </form>

        <div className="flex items-center gap-2">
          <select
            value={riskFilter}
            onChange={(e) => { setRiskFilter(e.target.value); setPage(1); }}
            className="px-3 py-2 bg-[#090f20] border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Risk Tiers</option>
            <option value="LOW">Low (0-29)</option>
            <option value="MEDIUM">Medium (30-59)</option>
            <option value="HIGH">High (60-79)</option>
            <option value="CRITICAL">Critical (80-100)</option>
          </select>

          <select
            value={channelFilter}
            onChange={(e) => { setChannelFilter(e.target.value); setPage(1); }}
            className="px-3 py-2 bg-[#090f20] border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Channels</option>
            <option value="MOBILE_APP">Mobile App</option>
            <option value="NET_BANKING">Net Banking</option>
            <option value="UPI">UPI Payment</option>
            <option value="POS_TERMINAL">POS Terminal</option>
            <option value="ATM">ATM</option>
          </select>

          <button
            onClick={() => { setSearch(''); setRiskFilter(''); setChannelFilter(''); setPage(1); }}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
            title="Reset filters"
          >
            <RefreshCw size={15} />
          </button>
        </div>
      </div>

      {/* Main Ledger Table */}
      <div className="rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#090f20] border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Transaction Ref</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Customer ID</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Channel</th>
                <th className="py-3 px-4">Merchant Cat</th>
                <th className="py-3 px-4">Country</th>
                <th className="py-3 px-4">Risk Assessment</th>
                <th className="py-3 px-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-500">
                    <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                    Fetching ledger records...
                  </td>
                </tr>
              ) : transactions.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-500">
                    No transactions match current filters.
                  </td>
                </tr>
              ) : (
                transactions.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-semibold text-white">{t.transaction_ref}</td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {new Date(t.timestamp).toLocaleDateString()} {new Date(t.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-cyan-400">{t.customer_id}</td>
                    <td className="py-3.5 px-4 font-bold text-white">₹{t.amount.toLocaleString()}</td>
                    <td className="py-3.5 px-4 text-slate-400">{t.payment_channel}</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                        {t.merchant_category}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">{t.country}</td>
                    <td className="py-3.5 px-4">
                      <RiskBadge category={t.risk_category} score={t.risk_score} />
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => setSelectedTxn(t)}
                        className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white transition-colors"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="p-4 bg-[#090f20] border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span>Showing page {page} of {Math.max(1, Math.ceil(total / pageSize))} ({total} total records)</span>
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
              disabled={page * pageSize >= total}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Synthetic Generation Modal */}
      {showGenModal && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0e162f] border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-base font-bold text-white mb-1 flex items-center gap-2">
              <Sparkles size={18} className="text-cyan-400" />
              <span>Simulate Synthetic Banking Flow</span>
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Injects realistic synthetic transactions with multi-vector fraud patterns for demo and stress testing.
            </p>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Transaction Count: {genCount}</label>
                <input
                  type="range"
                  min="10"
                  max="200"
                  step="10"
                  value={genCount}
                  onChange={(e) => setGenCount(e.target.value)}
                  className="w-full accent-blue-500 cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">
                  Fraud Pattern Ratio: {(genFraudRatio * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="0.05"
                  max="0.50"
                  step="0.05"
                  value={genFraudRatio}
                  onChange={(e) => setGenFraudRatio(e.target.value)}
                  className="w-full accent-rose-500 cursor-pointer"
                />
                <span className="text-[10px] text-slate-500">Injects velocity anomalies, geo impossible travel, and off-hour spikes.</span>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2">
              <button
                onClick={() => setShowGenModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleGenerateSynthetic}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/30"
              >
                Start Simulation
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Transaction Inspection Drawer / Modal */}
      {selectedTxn && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0e162f] border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl overflow-y-auto max-h-[90vh]">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <span>Transaction Risk Intelligence Report</span>
                </h3>
                <p className="text-xs text-slate-400 font-mono">{selectedTxn.transaction_ref}</p>
              </div>
              <RiskBadge category={selectedTxn.risk_category} score={selectedTxn.risk_score} />
            </div>

            {/* Behavioral & Core Profile Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-3.5 rounded-xl bg-[#090f20] border border-slate-800 text-xs mb-4">
              <div>
                <span className="text-slate-500 block">Customer ID</span>
                <span className="font-mono font-semibold text-cyan-400">{selectedTxn.customer_id}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Execution Amount</span>
                <span className="font-bold text-white">₹{selectedTxn.amount.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-slate-500 block">30-Day Customer Baseline</span>
                <span className="text-slate-300">₹{selectedTxn.historical_amount_avg?.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Channel / Type</span>
                <span className="text-slate-300">{selectedTxn.payment_channel} ({selectedTxn.transaction_type})</span>
              </div>
              <div>
                <span className="text-slate-500 block">Velocity (Past 1 Hour)</span>
                <span className="font-semibold text-amber-400">{selectedTxn.historical_velocity_1h} transactions</span>
              </div>
              <div>
                <span className="text-slate-500 block">Distance From Home</span>
                <span className="text-slate-300">{selectedTxn.distance_from_home_km} km</span>
              </div>
              <div>
                <span className="text-slate-500 block">IP Risk Score</span>
                <span className="text-slate-300">{selectedTxn.ip_risk_score} / 100</span>
              </div>
              <div>
                <span className="text-slate-500 block">Failed Security Attempts</span>
                <span className="text-slate-300">{selectedTxn.failed_attempts_count}</span>
              </div>
              <div>
                <span className="text-slate-500 block">ML Fraud Confidence</span>
                <span className="font-semibold text-rose-400">{(selectedTxn.ml_probability * 100).toFixed(1)}%</span>
              </div>
            </div>

            {/* AI Explainability Factors */}
            <div className="mb-4">
              <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Triggered Anomaly Indicators & Explainable Drivers:
              </h4>
              <div className="space-y-2">
                {(() => {
                  try {
                    const reasons = JSON.parse(selectedTxn.reasons || '[]');
                    if (!reasons.length) return <p className="text-xs text-slate-500">No anomalous risk vectors detected.</p>;
                    return reasons.map((r, i) => (
                      <div key={i} className="p-3 rounded-xl bg-rose-950/30 border border-rose-900/50 text-xs">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-bold text-rose-300">{r.factor}</span>
                          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-rose-900 text-rose-200 uppercase">{r.severity}</span>
                        </div>
                        <p className="text-slate-300 text-[11px] leading-relaxed">{r.description}</p>
                      </div>
                    ));
                  } catch (e) {
                    return <p className="text-xs text-slate-400">Baseline clean.</p>;
                  }
                })()}
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t border-slate-800">
              <button
                onClick={() => setSelectedTxn(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-colors"
              >
                Close Window
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
