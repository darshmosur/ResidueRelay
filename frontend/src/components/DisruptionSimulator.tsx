import React from 'react';
import { CloudRain, Wrench, RefreshCw, Zap, CheckCircle2, Play, AlertCircle } from 'lucide-react';
import { SimulationState } from '../lib/types';

interface DisruptionSimulatorProps {
  state: SimulationState | null;
  loading: boolean;
  onGenerate: () => void;
  onDisrupt: (preset: 'rain' | 'breakdown' | 'both') => void;
  onReplan: () => void;
  onApprove: () => void;
}

export const DisruptionSimulator: React.FC<DisruptionSimulatorProps> = ({
  state,
  loading,
  onGenerate,
  onDisrupt,
  onReplan,
  onApprove,
}) => {
  const scenario = state?.scenario || 'initial';
  const hasPlan = Boolean(state?.current_plan);
  const isApproved = state?.current_plan?.status === 'approved';
  const disruptions = state?.active_disruptions || [];

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <span>🎮 Demo Simulation Mission Control</span>
            <span className="text-xs font-normal text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full border border-slate-200">
              Interactive Testbed
            </span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Trigger real-world harvest bottlenecks and watch OR-Tools dynamically replan with human-in-the-loop approval.
          </p>
        </div>

        {/* Live Scenario Badge */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-slate-400">Current Phase:</span>
          <span className={`text-xs font-semibold px-2.5 py-1 rounded-lg border ${
            scenario === 'initial'
              ? 'bg-slate-100 text-slate-700 border-slate-200'
              : scenario === 'scheduled'
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
              : scenario === 'disrupted'
              ? 'bg-red-50 text-red-700 border-red-200 animate-pulse'
              : 'bg-amber-50 text-amber-800 border-amber-300'
          }`}>
            {scenario === 'initial' && 'Phase 1: Awaiting Generation'}
            {scenario === 'scheduled' && 'Phase 2: Baseline Plan Active'}
            {scenario === 'disrupted' && 'Phase 3: Field Disruptions Injected'}
            {scenario === 'replanned' && 'Phase 4: Dynamic Replan Active'}
          </span>
        </div>
      </div>

      {/* Action Buttons Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2.5">
        {/* Button 1: Generate Initial Plan */}
        <button
          onClick={onGenerate}
          disabled={loading || (hasPlan && scenario !== 'initial')}
          className={`flex flex-col items-center justify-center p-3 rounded-xl border text-center transition-all ${
            !hasPlan
              ? 'bg-emerald-600 hover:bg-emerald-700 text-white border-emerald-700 shadow-sm shadow-emerald-500/20 font-semibold ring-2 ring-emerald-400/30'
              : 'bg-slate-50 text-slate-400 border-slate-200 cursor-not-allowed opacity-60'
          }`}
        >
          <Play className="w-5 h-5 mb-1.5" />
          <span className="text-xs font-semibold">1. Generate Plan</span>
          <span className="text-[10px] opacity-80 mt-0.5">OR-Tools Solver</span>
        </button>

        {/* Button 2: Rain Disruption */}
        <button
          onClick={() => onDisrupt('rain')}
          disabled={loading || !hasPlan}
          className="flex flex-col items-center justify-center p-3 rounded-xl border border-sky-200 bg-sky-50/70 hover:bg-sky-100 text-sky-900 transition-all text-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <CloudRain className="w-5 h-5 text-sky-600 mb-1.5" />
          <span className="text-xs font-semibold">🌧️ Rain (+18h)</span>
          <span className="text-[10px] text-sky-700 mt-0.5">Taraori Cluster</span>
        </button>

        {/* Button 3: Baler Breakdown */}
        <button
          onClick={() => onDisrupt('breakdown')}
          disabled={loading || !hasPlan}
          className="flex flex-col items-center justify-center p-3 rounded-xl border border-red-200 bg-red-50/70 hover:bg-red-100 text-red-900 transition-all text-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Wrench className="w-5 h-5 text-red-600 mb-1.5" />
          <span className="text-xs font-semibold">⚠️ Baler 2 Down</span>
          <span className="text-[10px] text-red-700 mt-0.5">Hydraulic Pump</span>
        </button>

        {/* Button 4: Dual Storm & Failure */}
        <button
          onClick={() => onDisrupt('both')}
          disabled={loading || !hasPlan}
          className="flex flex-col items-center justify-center p-3 rounded-xl border border-rose-300 bg-rose-100/60 hover:bg-rose-200/80 text-rose-950 transition-all text-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Zap className="w-5 h-5 text-rose-600 mb-1.5" />
          <span className="text-xs font-semibold">⚡ Dual Disruption</span>
          <span className="text-[10px] text-rose-700 mt-0.5">Rain + Breakdown</span>
        </button>

        {/* Button 5: Replan */}
        <button
          onClick={onReplan}
          disabled={loading || !hasPlan}
          className={`flex flex-col items-center justify-center p-3 rounded-xl border text-center transition-all ${
            scenario === 'disrupted'
              ? 'bg-amber-500 hover:bg-amber-600 text-slate-950 border-amber-600 shadow-md ring-2 ring-amber-300 animate-pulse font-bold'
              : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100 disabled:opacity-50'
          }`}
        >
          <RefreshCw className={`w-5 h-5 mb-1.5 text-amber-700 ${loading ? 'animate-spin' : ''}`} />
          <span className="text-xs font-semibold">2. Re-Optimize</span>
          <span className="text-[10px] text-slate-500 mt-0.5">Minimal Churn</span>
        </button>

        {/* Button 6: Approve Plan */}
        <button
          onClick={onApprove}
          disabled={loading || !hasPlan || isApproved}
          className={`flex flex-col items-center justify-center p-3 rounded-xl border text-center transition-all ${
            hasPlan && !isApproved
              ? 'bg-emerald-600 hover:bg-emerald-700 text-white border-emerald-700 shadow-sm font-bold ring-2 ring-emerald-400'
              : 'bg-slate-50 text-slate-400 border-slate-200 cursor-not-allowed opacity-60'
          }`}
        >
          <CheckCircle2 className="w-5 h-5 mb-1.5 text-emerald-200" />
          <span className="text-xs font-semibold">3. Approve Plan</span>
          <span className="text-[10px] opacity-80 mt-0.5">{isApproved ? 'Approved ✓' : 'Human Sign-off'}</span>
        </button>
      </div>

      {/* Active Disruption Status Strip */}
      {disruptions.length > 0 && (
        <div className="mt-4 pt-3.5 border-t border-slate-100 flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-600 flex items-center gap-1">
            <AlertCircle className="w-3.5 h-3.5 text-amber-500" />
            Active Bottlenecks:
          </span>
          {disruptions.map((d, i) => (
            <div
              key={d.id || i}
              className={`text-xs px-2.5 py-1 rounded-md flex items-center gap-1.5 border font-medium ${
                d.type === 'baler_breakdown'
                  ? 'bg-red-50 text-red-800 border-red-200'
                  : 'bg-sky-50 text-sky-800 border-sky-200'
              }`}
            >
              <span>{d.type === 'baler_breakdown' ? '🚜 ⚠️' : '🌧️'}</span>
              <span>{d.description}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
