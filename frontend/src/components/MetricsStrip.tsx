import React from 'react';
import { SimulationState } from '../lib/types';
import { Flame, Trees, Clock, CheckCircle, Truck, AlertTriangle } from 'lucide-react';

interface MetricsStripProps {
  state: SimulationState | null;
}

export const MetricsStrip: React.FC<MetricsStripProps> = ({ state }) => {
  const plan = state?.current_plan;
  const metrics = plan?.metrics;
  const activeBalers = state?.balers.filter(b => b.status === 'available' || b.status === 'busy').length ?? 3;
  const brokenBalers = state?.balers.filter(b => b.status === 'broken_down').length ?? 0;

  const totalAcres = metrics ? metrics.total_acres : state?.farms.reduce((acc, f) => acc + f.acres, 0) ?? 115.5;
  const totalStrawTons = metrics ? metrics.total_straw_tons : Math.round(totalAcres * 2.25);
  const scheduledCount = metrics ? metrics.scheduled_farms : 0;
  const totalFarms = state?.farms.length ?? 15;
  const avgDelay = metrics ? `${metrics.avg_delay_hours}h` : '—';
  const co2Avoided = metrics ? `${metrics.co2_avoided_tons} T` : `${Math.round(totalStrawTons * 1.5)} T`;
  const burningRiskPct = metrics ? metrics.burning_risk_pct : 0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {/* 1. Residue Scheduled */}
      <div className="bg-white rounded-xl p-3.5 border border-slate-200/80 shadow-sm flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-500 mb-1">
          <span className="text-xs font-semibold uppercase tracking-wider">Residue Straw</span>
          <span className="p-1.5 bg-emerald-50 rounded-lg text-emerald-600">🌾</span>
        </div>
        <div>
          <div className="text-xl font-bold text-slate-900">{totalStrawTons} <span className="text-xs font-normal text-slate-500">Tons</span></div>
          <div className="text-[11px] text-slate-500 mt-0.5">{totalAcres} acres paddy</div>
        </div>
      </div>

      {/* 2. Coverage / Farm Count */}
      <div className="bg-white rounded-xl p-3.5 border border-slate-200/80 shadow-sm flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-500 mb-1">
          <span className="text-xs font-semibold uppercase tracking-wider">Farms Scheduled</span>
          <CheckCircle className="w-4 h-4 text-emerald-500" />
        </div>
        <div>
          <div className="text-xl font-bold text-slate-900">
            {scheduledCount} <span className="text-xs font-normal text-slate-400">/ {totalFarms}</span>
          </div>
          <div className="text-[11px] text-emerald-600 font-medium mt-0.5">
            {scheduledCount === totalFarms ? '100% Fields Coordinated' : `${totalFarms - scheduledCount} pending`}
          </div>
        </div>
      </div>

      {/* 3. CO2 Offset */}
      <div className="bg-white rounded-xl p-3.5 border border-slate-200/80 shadow-sm flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-500 mb-1">
          <span className="text-xs font-semibold uppercase tracking-wider">CO₂ Offset</span>
          <Trees className="w-4 h-4 text-green-600" />
        </div>
        <div>
          <div className="text-xl font-bold text-slate-900">{co2Avoided}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Vs. open-field burning</div>
        </div>
      </div>

      {/* 4. Burning Risk */}
      <div className={`rounded-xl p-3.5 border shadow-sm flex flex-col justify-between transition-colors ${
        burningRiskPct > 0 
          ? 'bg-red-50 border-red-200 text-red-950' 
          : 'bg-white border-slate-200/80'
      }`}>
        <div className="flex items-center justify-between mb-1">
          <span className={`text-xs font-semibold uppercase tracking-wider ${burningRiskPct > 0 ? 'text-red-700' : 'text-slate-500'}`}>
            Burning Risk
          </span>
          <Flame className={`w-4 h-4 ${burningRiskPct > 0 ? 'text-red-600 animate-bounce' : 'text-slate-400'}`} />
        </div>
        <div>
          <div className={`text-xl font-bold ${burningRiskPct > 0 ? 'text-red-600' : 'text-emerald-600'}`}>
            {burningRiskPct}%
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            {burningRiskPct === 0 ? 'All sowing deadlines met' : 'At risk of farmer burning'}
          </div>
        </div>
      </div>

      {/* 5. Avg Delay */}
      <div className="bg-white rounded-xl p-3.5 border border-slate-200/80 shadow-sm flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-500 mb-1">
          <span className="text-xs font-semibold uppercase tracking-wider">Avg Delay</span>
          <Clock className="w-4 h-4 text-amber-500" />
        </div>
        <div>
          <div className="text-xl font-bold text-slate-900">{avgDelay}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Harvest to baler pickup</div>
        </div>
      </div>

      {/* 6. Active Baler Fleet */}
      <div className="bg-white rounded-xl p-3.5 border border-slate-200/80 shadow-sm flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-500 mb-1">
          <span className="text-xs font-semibold uppercase tracking-wider">Baler Fleet</span>
          <Truck className="w-4 h-4 text-blue-500" />
        </div>
        <div>
          <div className="text-xl font-bold text-slate-900">
            {activeBalers} <span className="text-xs font-normal text-slate-400">/ 3 Online</span>
          </div>
          <div className="text-[11px] mt-0.5">
            {brokenBalers > 0 ? (
              <span className="text-red-600 font-semibold flex items-center gap-1">
                <AlertTriangle className="w-3 h-3 inline" /> 1 Baler Broken Down
              </span>
            ) : (
              <span className="text-slate-500">All depots operational</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
