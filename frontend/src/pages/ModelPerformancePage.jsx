import React, { useState, useEffect } from 'react';
import {
  Cpu, Award, BarChart2, CheckCircle2, AlertTriangle, Layers,
  Sliders, RefreshCw, Sparkles, BookOpen
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer
} from 'recharts';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

export const ModelPerformancePage = () => {
  const [metrics, setMetrics] = useState(null);
  const [comparison, setComparison] = useState([]);
  const [loading, setLoading] = useState(true);
  const [threshold, setThreshold] = useState(0.48);
  const [retraining, setRetraining] = useState(false);
  const { isAdmin } = useAuth();

  const fetchModelData = async () => {
    setLoading(true);
    try {
      const [metricsRes, compRes] = await Promise.all([
        api.get('/ml/metrics'),
        api.get('/ml/comparison')
      ]);
      setMetrics(metricsRes.data);
      setComparison(compRes.data);
      if (metricsRes.data.decision_threshold) {
        setThreshold(metricsRes.data.decision_threshold);
      }
    } catch (err) {
      console.error('Error fetching model performance:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModelData();
  }, []);

  const handleRetrain = async () => {
    if (!isAdmin) {
      alert('Only administrators can trigger pipeline retraining.');
      return;
    }
    setRetraining(true);
    try {
      await api.post('/ml/retrain');
      alert('Random Forest Model retrained and refreshed successfully!');
      fetchModelData();
    } catch (err) {
      alert('Retrain error: ' + (err.response?.data?.detail || err.message));
    } finally {
      setRetraining(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const cm = metrics?.confusion_matrix || { true_positives: 0, false_positives: 0, true_negatives: 0, false_negatives: 0 };
  const featureImportances = metrics?.feature_importances || [];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <span>Machine Learning Model Governance</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Offline benchmark validation on held-out test splits, PR-AUC curve, and explainability feature weights
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRetrain}
            disabled={retraining}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold rounded-xl shadow-md transition-all active:scale-95 disabled:opacity-50"
          >
            <RefreshCw size={14} className={retraining ? 'animate-spin' : ''} />
            <span>{retraining ? 'Retraining Model...' : 'Retrain Random Forest'}</span>
          </button>
        </div>
      </div>

      {/* Model Spec & Primary Test Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="p-4 rounded-xl bg-[#0e162f] border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">Precision</span>
          <div className="text-xl font-bold text-white mt-1">{(metrics?.precision * 100).toFixed(1)}%</div>
          <span className="text-[10px] text-slate-500">Low false alarm rate</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e162f] border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">Recall</span>
          <div className="text-xl font-bold text-cyan-400 mt-1">{(metrics?.recall * 100).toFixed(1)}%</div>
          <span className="text-[10px] text-slate-500">Fraud capture rate</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e162f] border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">F1-Score</span>
          <div className="text-xl font-bold text-emerald-400 mt-1">{(metrics?.f1_score * 100).toFixed(1)}%</div>
          <span className="text-[10px] text-slate-500">Harmonic balance</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e162f] border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">PR-AUC</span>
          <div className="text-xl font-bold text-amber-400 mt-1">{(metrics?.pr_auc * 100).toFixed(1)}%</div>
          <span className="text-[10px] text-slate-500">Precision-Recall Area</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e162f] border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">ROC-AUC</span>
          <div className="text-xl font-bold text-indigo-400 mt-1">{(metrics?.roc_auc * 100).toFixed(1)}%</div>
          <span className="text-[10px] text-slate-500">True vs False positive</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e162f] border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">Overall Acc</span>
          <div className="text-xl font-bold text-slate-300 mt-1">{(metrics?.accuracy * 100).toFixed(1)}%</div>
          <span className="text-[10px] text-slate-500">{metrics?.test_samples_count} test items</span>
        </div>
      </div>

      {/* Class Imbalance Technical Note for Interviewers */}
      <div className="p-4 rounded-xl bg-blue-950/40 border border-blue-800/40 text-xs text-blue-200 flex items-start gap-3">
        <BookOpen size={18} className="text-cyan-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-white">Engineering Note on Banking Class Imbalance:</span>
          <p className="mt-0.5 text-slate-300 leading-relaxed text-[11px]">
            In authentic financial datasets, fraudulent transactions typically constitute less than 1-2% of total transaction throughput.
            Consequently, raw Accuracy is a deceptive metric (a naive model predicting all transactions as legitimate would report 98%+ accuracy).
            FinGuard AI prioritizes <strong>PR-AUC</strong> and <strong>F1-Score</strong> with balanced class weighting and optimal decision threshold calibration.
          </p>
        </div>
      </div>

      {/* Confusion Matrix & Feature Importance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Confusion Matrix Visualizer */}
        <div className="p-5 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white mb-1">Held-Out Test Confusion Matrix</h3>
            <p className="text-[11px] text-slate-400 mb-4">Actual vs Predicted classification outcomes</p>

            <div className="grid grid-cols-2 gap-3 p-4 bg-[#090f20] rounded-xl border border-slate-800">
              <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-800/50 text-center">
                <span className="text-[10px] text-slate-400 font-semibold block uppercase">True Negatives (TN)</span>
                <span className="text-2xl font-bold text-emerald-400 mt-1 block">{cm.true_negatives}</span>
                <span className="text-[10px] text-emerald-300/80">Legitimate approved cleanly</span>
              </div>

              <div className="p-4 rounded-xl bg-amber-950/40 border border-amber-800/50 text-center">
                <span className="text-[10px] text-slate-400 font-semibold block uppercase">False Positives (FP)</span>
                <span className="text-2xl font-bold text-amber-400 mt-1 block">{cm.false_positives}</span>
                <span className="text-[10px] text-amber-300/80">Analyst review required</span>
              </div>

              <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/50 text-center">
                <span className="text-[10px] text-slate-400 font-semibold block uppercase">False Negatives (FN)</span>
                <span className="text-2xl font-bold text-rose-400 mt-1 block">{cm.false_negatives}</span>
                <span className="text-[10px] text-rose-300/80">Missed anomalies</span>
              </div>

              <div className="p-4 rounded-xl bg-blue-950/40 border border-blue-800/50 text-center">
                <span className="text-[10px] text-slate-400 font-semibold block uppercase">True Positives (TP)</span>
                <span className="text-2xl font-bold text-blue-400 mt-1 block">{cm.true_positives}</span>
                <span className="text-[10px] text-blue-300/80">Fraud attacks thwarted</span>
              </div>
            </div>
          </div>
        </div>

        {/* Feature Importance Bar Chart */}
        <div className="p-5 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg">
          <h3 className="text-sm font-semibold text-white mb-1">Random Forest Feature Weight Ranking</h3>
          <p className="text-[11px] text-slate-400 mb-4">Gini impurity decrease attributed to key behavioural attributes</p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={featureImportances.slice(0, 6)}
                layout="vertical"
                margin={{ top: 5, right: 20, left: 40, bottom: 5 }}
              >
                <XAxis type="number" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis dataKey="feature" type="category" stroke="#64748b" fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090f20', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                />
                <Bar dataKey="importance" fill="#06b6d4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Model Comparison Table */}
      <div className="p-5 rounded-2xl bg-[#0e162f] border border-slate-800 shadow-lg">
        <h3 className="text-sm font-semibold text-white mb-1">System Architecture Comparison: Rules vs ML</h3>
        <p className="text-[11px] text-slate-400 mb-4">
          Evaluating deterministic baseline rules against machine learning models and hybrid ensemble
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#090f20] border-b border-slate-800 text-slate-400 font-semibold uppercase">
              <tr>
                <th className="py-3 px-4">Methodology</th>
                <th className="py-3 px-4">Precision</th>
                <th className="py-3 px-4">Recall</th>
                <th className="py-3 px-4">F1-Score</th>
                <th className="py-3 px-4">Inference Latency</th>
                <th className="py-3 px-4">Explainability Mechanism</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {comparison.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 font-bold text-white">{item.method}</td>
                  <td className="py-3 px-4 text-emerald-400 font-semibold">{(item.precision * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4 text-cyan-400 font-semibold">{(item.recall * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4 text-amber-400 font-semibold">{(item.f1_score * 100).toFixed(1)}%</td>
                  <td className="py-3 px-4 text-slate-400">{item.latency_ms} ms</td>
                  <td className="py-3 px-4 text-[11px] text-slate-300">{item.explainability}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
