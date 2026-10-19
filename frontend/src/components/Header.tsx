import React from 'react';
import { RotateCcw, Sparkles, CheckCircle2, AlertTriangle, CloudRain, ShieldCheck } from 'lucide-react';
import { SimulationState } from '../lib/types';

interface HeaderProps {
  state: SimulationState | null;
  onReset: () => void;
  loading: boolean;
}

export const Header: React.FC<HeaderProps> = ({ state, onReset, loading }) => {
  const scenario = state?.scenario || 'initial';
  const planVersion = state?.current_plan?.version;
  const isApproved = state?.current_plan?.status === 'approved';

  return (
    <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-green-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <span className="text-xl font-black text-slate-950">🌾</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight text-white">ResidueRelay</h1>
              <span className="text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded-full uppercase tracking-wider">
                Hackathon Demo
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Autonomous Paddy Residue & Harvester Fleet Coordination • Karnal District
            </p>
          </div>
        </div>

        {/* Workflow Stepper */}
        <div className="hidden lg:flex items-center space-x-2 bg-slate-800/80 border border-slate-700/60 rounded-xl p-1.5 text-xs">
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-lg transition-colors ${scenario === 'initial' ? 'bg-slate-700 text-white font-medium' : 'text-slate-400'}`}>
            <span className="w-4 h-4 rounded-full bg-slate-600 flex items-center justify-center text-[10px]">1</span>
            <span>Intake & Ready</span>
          </div>
          <span className="text-slate-600">→</span>

          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-lg transition-colors ${scenario === 'scheduled' ? 'bg-emerald-600/90 text-white font-medium shadow-sm' : 'text-slate-400'}`}>
            <span className="w-4 h-4 rounded-full bg-emerald-700 flex items-center justify-center text-[10px]">2</span>
            <span>Plan v1</span>
          </div>
          <span className="text-slate-600">→</span>

          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-lg transition-colors ${scenario === 'disrupted' ? 'bg-red-500/90 text-white font-medium shadow-sm animate-pulse' : 'text-slate-400'}`}>
            <span className="w-4 h-4 rounded-full bg-red-700 flex items-center justify-center text-[10px]">3</span>
            <span>Disruptions</span>
          </div>
          <span className="text-slate-600">→</span>

          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-lg transition-colors ${scenario === 'replanned' ? 'bg-amber-500/90 text-slate-950 font-bold shadow-sm' : 'text-slate-400'}`}>
            <span className="w-4 h-4 rounded-full bg-amber-600 flex items-center justify-center text-[10px] text-white">4</span>
            <span>Replan {planVersion ? `v${planVersion}` : ''} {isApproved ? '✓' : ''}</span>
          </div>
        </div>

        {/* Actions & Status */}
        <div className="flex items-center gap-3">
          {isApproved ? (
            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-lg text-xs font-medium">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Approved & Dispatched</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-amber-500/10 text-amber-300 border border-amber-500/30 rounded-lg text-xs font-medium">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
              <span>{planVersion ? `Plan v${planVersion} Pending` : 'Awaiting Plan'}</span>
            </div>
          )}

          <button
            onClick={onReset}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 active:bg-slate-600 text-slate-200 border border-slate-700 rounded-lg text-xs font-medium transition-colors shadow-sm disabled:opacity-50"
            title="Reset demonstration state back to original 15 farms"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Reset Demo</span>
          </button>
        </div>
      </div>
    </header>
  );
};
