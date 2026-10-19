import React from 'react';
import { SchedulePlan, SimulationState } from '../lib/types';
import { ShieldCheck, ArrowRight, AlertTriangle, Sparkles, CheckCircle2 } from 'lucide-react';

interface PlanDiffModalProps {
  state: SimulationState | null;
  onApprove: () => void;
  loading: boolean;
}

export const PlanDiffModal: React.FC<PlanDiffModalProps> = ({ state, onApprove, loading }) => {
  const currentPlan = state?.current_plan;
  const prevPlan = state?.previous_plan;
  if (!currentPlan) return null;

  const isPending = currentPlan.status === 'pending_approval';
  const isApproved = currentPlan.status === 'approved';

  // Calculate changes between prevPlan and currentPlan
  const changedJobs: Array<{ farmId: string; farmerName: string; oldBaler?: string; newBaler: string; oldStart?: number; newStart: number }> = [];
  if (prevPlan) {
    const prevMap = new Map(prevPlan.jobs.map(j => [j.farm_id, j]));
    currentPlan.jobs.forEach(currJob => {
      const prevJob = prevMap.get(currJob.farm_id);
      const farm = state?.farms.find(f => f.id === currJob.farm_id);
      if (prevJob) {
        if (prevJob.baler_id !== currJob.baler_id || Math.abs(prevJob.start_hour - currJob.start_hour) >= 1.5) {
          changedJobs.push({
            farmId: currJob.farm_id,
            farmerName: farm?.farmer_name || currJob.farm_id,
            oldBaler: prevJob.baler_id,
            newBaler: currJob.baler_id,
            oldStart: prevJob.start_hour,
            newStart: currJob.start_hour,
          });
        }
      }
    });
  }

  return (
    <div className={`rounded-2xl border p-5 transition-all shadow-sm ${
      isPending
        ? 'bg-gradient-to-r from-amber-500/10 via-amber-400/5 to-transparent border-amber-300'
        : 'bg-white border-slate-200/80'
    }`}>
      {/* Top Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-3.5 border-b border-slate-200/60">
        <div className="flex items-center gap-3">
          <div className={`w-9 h-9 rounded-xl flex items-center justify-center font-bold text-sm ${
            isPending ? 'bg-amber-500 text-slate-950 shadow-sm' : 'bg-emerald-600 text-white'
          }`}>
            v{currentPlan.version}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-900">
                Harvest Coordination Plan {currentPlan.plan_id.toUpperCase()}
              </h3>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border uppercase tracking-wider ${
                isPending
                  ? 'bg-amber-100 text-amber-900 border-amber-300 animate-pulse'
                  : 'bg-emerald-100 text-emerald-800 border-emerald-300'
              }`}>
                {isPending ? '⚠️ Human Approval Required' : '✓ Approved & Dispatched'}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              {isPending
                ? 'Review the constraint-optimized schedule changes below before confirming field dispatch orders.'
                : 'Plan is locked. Automated WhatsApp & SMS dispatch orders delivered to fleet operators.'}
            </p>
          </div>
        </div>

        {/* Action Button */}
        {isPending && (
          <button
            onClick={onApprove}
            disabled={loading}
            className="flex items-center justify-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white text-xs font-bold rounded-xl shadow-md shadow-emerald-600/20 transition-all cursor-pointer"
          >
            <ShieldCheck className="w-4 h-4 text-emerald-100" />
            <span>Approve & Issue Fleet Orders</span>
          </button>
        )}
      </div>

      {/* Narrative & Reassignment Diff */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 pt-4">
        {/* Left: AI Dispatch Narrative */}
        <div className="lg:col-span-2 bg-slate-50 rounded-xl p-4 border border-slate-200/70 text-xs">
          <div className="flex items-center gap-1.5 font-bold text-slate-800 mb-2">
            <Sparkles className="w-3.5 h-3.5 text-amber-600" />
            <span>AI Dispatch Brief & Operational Trade-offs</span>
          </div>

          <div className="prose prose-xs text-slate-600 max-w-none space-y-1.5 whitespace-pre-line font-mono text-[11px] leading-relaxed">
            {currentPlan.disruption_summary || currentPlan.ai_dispatch_brief || 'Standard baseline plan computed with zero conflicts.'}
          </div>
        </div>

        {/* Right: Reassigned Jobs Diff */}
        <div className="bg-slate-50 rounded-xl p-4 border border-slate-200/70 text-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold text-slate-800">Job Delta vs. Plan v1</span>
              <span className="text-[10px] font-mono text-slate-400">
                {changedJobs.length} Changes
              </span>
            </div>

            {changedJobs.length > 0 ? (
              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {changedJobs.map((cj, idx) => (
                  <div key={idx} className="p-2 rounded-lg bg-white border border-slate-200 text-[11px]">
                    <div className="font-semibold text-slate-900 truncate">{cj.farmerName}</div>
                    <div className="flex items-center gap-1.5 text-slate-500 mt-1">
                      <span className="font-mono bg-slate-100 px-1 rounded">{cj.oldBaler?.toUpperCase()}</span>
                      <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
                      <span className="font-mono bg-amber-100 text-amber-900 font-bold px-1 rounded">{cj.newBaler.toUpperCase()}</span>
                      <span className="text-slate-400 font-mono text-[10px] ml-auto">@{cj.newStart.toFixed(1)}h</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-6 text-center text-slate-400">
                <CheckCircle2 className="w-6 h-6 mx-auto text-emerald-500/60 mb-1" />
                <span>All assignments aligned with optimal baseline</span>
              </div>
            )}
          </div>

          <div className="mt-3 pt-2 border-t border-slate-200 text-[10px] text-slate-500 flex items-center justify-between">
            <span>Sowing Compliance: {100.0 - currentPlan.metrics.burning_risk_pct}%</span>
            <span>Avg Delay: {currentPlan.metrics.avg_delay_hours} hrs</span>
          </div>
        </div>
      </div>
    </div>
  );
};
