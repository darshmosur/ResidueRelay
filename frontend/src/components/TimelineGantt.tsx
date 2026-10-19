import React, { useState } from 'react';
import { SimulationState, Job, Baler, Farm, Buyer } from '../lib/types';
import { AlertTriangle, Clock, MapPin, Truck, ChevronRight, CheckCircle2, User, Phone } from 'lucide-react';

interface TimelineGanttProps {
  state: SimulationState | null;
}

export const TimelineGantt: React.FC<TimelineGanttProps> = ({ state }) => {
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  const plan = state?.current_plan;
  const balers = state?.balers || [];
  const farms = state?.farms || [];
  const buyers = state?.buyers || [];
  const jobs = plan?.jobs || [];

  const HORIZON_HOURS = 72; // 3 Days view
  const HOURS_PER_DAY = 24;

  const getFarm = (farmId: string): Farm | undefined => farms.find(f => f.id === farmId);
  const getBuyer = (buyerId: string): Buyer | undefined => buyers.find(b => b.id === buyerId);
  const getBaler = (balerId: string): Baler | undefined => balers.find(b => b.id === balerId);

  // Time markers (Every 6 hours)
  const timeMarkers = [];
  for (let h = 0; h <= HORIZON_HOURS; h += 6) {
    const day = Math.floor(h / 24) + 1;
    const hourOfDay = h % 24;
    timeMarkers.push({
      totalHours: h,
      label: `D${day} ${hourOfDay.toString().padStart(2, '0')}:00`,
      isDayStart: hourOfDay === 0,
      isDaylightStart: hourOfDay === 7,
      isDaylightEnd: hourOfDay === 19,
    });
  }

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden flex flex-col">
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3 bg-slate-50/50">
        <div>
          <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <span>📅 Fleet Gantt Schedule & Machine Utilization</span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
              {jobs.length} Active Assignments
            </span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Synchronized 72-hour operational timeline respecting daylight working hours (07:00–19:00) and transit routes.
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-xs text-slate-600">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-emerald-600 inline-block shadow-xs" />
            <span>Optimal</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-amber-500 inline-block shadow-xs" />
            <span>Dynamically Rescheduled</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-red-500 inline-block shadow-xs animate-pulse" />
            <span>Disrupted Bottleneck</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-slate-200 inline-block" />
            <span>🌙 Night Buffer</span>
          </div>
        </div>
      </div>

      {/* Gantt Container */}
      <div className="overflow-x-auto min-w-full pb-4">
        <div className="min-w-[900px] px-5 pt-3">
          {/* Timeline Header (Time axis) */}
          <div className="relative h-7 border-b border-slate-200 mb-2 ml-48">
            {timeMarkers.map(m => {
              const leftPct = (m.totalHours / HORIZON_HOURS) * 100;
              return (
                <div
                  key={m.totalHours}
                  className="absolute top-0 transform -translate-x-1/2 flex flex-col items-center"
                  style={{ left: `${leftPct}%` }}
                >
                  <span className={`text-[10px] font-mono font-medium ${m.isDayStart ? 'text-slate-900 font-bold' : 'text-slate-400'}`}>
                    {m.label}
                  </span>
                  <div className={`w-px ${m.isDayStart ? 'h-3 bg-slate-400' : 'h-1.5 bg-slate-200'}`} />
                </div>
              );
            })}
          </div>

          {/* Baler Rows */}
          <div className="space-y-4">
            {balers.map(baler => {
              const balerJobs = jobs.filter(j => j.baler_id === baler.id);
              const isBroken = baler.status === 'broken_down';
              const breakdownHour = baler.breakdown_time_hours ?? 10.0;

              return (
                <div key={baler.id} className="flex items-stretch border border-slate-200/90 rounded-xl bg-slate-50/30 overflow-hidden shadow-2xs">
                  {/* Left: Baler Info Column */}
                  <div className="w-48 shrink-0 p-3 bg-slate-100/80 border-r border-slate-200 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-900 font-mono">{baler.id.toUpperCase()}</span>
                        {isBroken ? (
                          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-red-100 text-red-700 border border-red-300">
                            OFFLINE
                          </span>
                        ) : (
                          <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700">
                            READY
                          </span>
                        )}
                      </div>
                      <div className="text-xs font-semibold text-slate-800 mt-1 flex items-center gap-1">
                        <User className="w-3 h-3 text-slate-500" />
                        <span className="truncate">{baler.operator_name}</span>
                      </div>
                      <div className="text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-slate-400" />
                        <span className="truncate">{baler.depot_location.lat > 29.85 ? 'Indri Depot' : baler.depot_location.lat > 29.82 ? 'Nilokheri' : 'Taraori'}</span>
                      </div>
                    </div>

                    <div className="text-[10px] text-slate-500 font-mono mt-2 pt-1 border-t border-slate-200 flex items-center justify-between">
                      <span>Rate: {baler.throughput_acres_per_hour} ac/h</span>
                      <span>{balerJobs.length} jobs</span>
                    </div>
                  </div>

                  {/* Right: Gantt Track */}
                  <div className="relative grow h-24 bg-white">
                    {/* Night time background bands */}
                    {[0, 1, 2].map(day => {
                      const nightStartH = day * 24 + 19;
                      const nightEndH = (day + 1) * 24 + 7;
                      if (nightStartH >= HORIZON_HOURS) return null;
                      const leftPct = (nightStartH / HORIZON_HOURS) * 100;
                      const widthPct = (Math.min(nightEndH, HORIZON_HOURS) - nightStartH) / HORIZON_HOURS * 100;
                      return (
                        <div
                          key={day}
                          className="absolute top-0 bottom-0 bg-slate-100/70 border-x border-slate-200/60 flex items-center justify-center text-[10px] text-slate-400 font-mono select-none"
                          style={{ left: `${leftPct}%`, width: `${widthPct}%` }}
                        >
                          <span className="rotate-90 sm:rotate-0">🌙 Night</span>
                        </div>
                      );
                    })}

                    {/* Breakdown Overlay if this baler is broken */}
                    {isBroken && (
                      <div
                        className="absolute top-0 bottom-0 right-0 bg-red-500/15 border-l-2 border-red-500 backdrop-blur-2xs flex items-center justify-center z-10"
                        style={{ left: `${(breakdownHour / HORIZON_HOURS) * 100}%` }}
                      >
                        <div className="bg-red-600 text-white text-[11px] font-bold px-2.5 py-1 rounded-md shadow-md flex items-center gap-1.5 border border-red-700">
                          <AlertTriangle className="w-3.5 h-3.5" />
                          <span>BREAKDOWN (Hour {breakdownHour}:00) — Offline</span>
                        </div>
                      </div>
                    )}

                    {/* Job Pills */}
                    {balerJobs.map(job => {
                      const farm = getFarm(job.farm_id);
                      const buyer = getBuyer(job.buyer_id);
                      const leftPct = (job.start_hour / HORIZON_HOURS) * 100;
                      const widthPct = Math.max(2.5, (job.duration_hours / HORIZON_HOURS) * 100);

                      const isDisrupted = job.status === 'disrupted';
                      const isReassigned = state?.scenario === 'replanned' && (state?.previous_plan?.jobs.find(pj => pj.farm_id === job.farm_id)?.baler_id !== job.baler_id);

                      let pillBg = 'bg-gradient-to-r from-emerald-600 to-emerald-500 text-white border-emerald-700 hover:from-emerald-700 hover:to-emerald-600';
                      if (isDisrupted) {
                        pillBg = 'bg-red-500 text-white border-red-700 animate-pulse ring-2 ring-red-300';
                      } else if (isReassigned) {
                        pillBg = 'bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 font-bold border-amber-600 shadow-md ring-2 ring-amber-300';
                      }

                      return (
                        <div
                          key={job.id}
                          onClick={() => setSelectedJob(job)}
                          className={`absolute top-2.5 bottom-2.5 rounded-lg border px-2 py-1 flex flex-col justify-between cursor-pointer transition-transform hover:scale-105 hover:z-20 shadow-xs ${pillBg}`}
                          style={{
                            left: `${leftPct}%`,
                            width: `${widthPct}%`,
                            minWidth: '70px',
                          }}
                          title={`Farm: ${farm?.farmer_name} (${farm?.acres} acres) -> Buyer: ${buyer?.name}`}
                        >
                          <div className="flex items-center justify-between text-[11px] leading-tight font-bold truncate">
                            <span className="truncate">{farm?.farmer_name.split(' ')[0]}</span>
                            <span className="text-[10px] opacity-90">{farm?.acres}ac</span>
                          </div>

                          <div className="flex items-center justify-between text-[9px] opacity-90 truncate">
                            <span className="truncate">{farm?.village}</span>
                            <span className="truncate font-mono">{job.start_hour.toFixed(1)}h</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Selected Job Detail Modal/Drawer */}
      {selectedJob && (
        <div className="fixed inset-0 bg-slate-950/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-5 border border-slate-200 shadow-xl animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Harvest Job Card</span>
                <h3 className="text-base font-bold text-slate-900">{getFarm(selectedJob.farm_id)?.farmer_name}</h3>
              </div>
              <button
                onClick={() => setSelectedJob(null)}
                className="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center text-xs font-bold"
              >
                ✕
              </button>
            </div>

            <div className="py-4 space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2 bg-slate-50 p-3 rounded-xl border border-slate-100">
                <div>
                  <span className="text-slate-400">Village:</span>
                  <div className="font-semibold text-slate-800">{getFarm(selectedJob.farm_id)?.village} ({getFarm(selectedJob.farm_id)?.cluster})</div>
                </div>
                <div>
                  <span className="text-slate-400">Field Size:</span>
                  <div className="font-semibold text-slate-800">{getFarm(selectedJob.farm_id)?.acres} Acres (~{selectedJob.straw_tons} Tons)</div>
                </div>
                <div>
                  <span className="text-slate-400">Scheduled Start:</span>
                  <div className="font-semibold text-slate-800">Hour {selectedJob.start_hour} (Duration: {selectedJob.duration_hours}h)</div>
                </div>
                <div>
                  <span className="text-slate-400">Sowing Deadline:</span>
                  <div className="font-semibold text-slate-800">Hour {getFarm(selectedJob.farm_id)?.sowing_deadline_hours}</div>
                </div>
              </div>

              <div>
                <span className="text-slate-400">Assigned Baler & Operator:</span>
                <div className="font-semibold text-slate-800 flex items-center gap-1.5 mt-0.5">
                  <Truck className="w-3.5 h-3.5 text-blue-500" />
                  <span>{getBaler(selectedJob.baler_id)?.operator_name} ({selectedJob.baler_id.toUpperCase()})</span>
                </div>
              </div>

              <div>
                <span className="text-slate-400">Designated Straw Off-Taker:</span>
                <div className="font-semibold text-slate-800 flex items-center gap-1.5 mt-0.5">
                  <span className="w-3.5 h-3.5 text-center">🏭</span>
                  <span>{getBuyer(selectedJob.buyer_id)?.name}</span>
                </div>
                <div className="text-[11px] text-emerald-600 font-medium">Rate: ₹{getBuyer(selectedJob.buyer_id)?.price_per_ton}/ton</div>
              </div>

              {selectedJob.disruption_note && (
                <div className="bg-red-50 border border-red-200 text-red-900 p-2.5 rounded-lg text-xs flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold">Disruption Notice:</span>
                    <p className="mt-0.5">{selectedJob.disruption_note}</p>
                  </div>
                </div>
              )}
            </div>

            <div className="pt-2 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setSelectedJob(null)}
                className="px-4 py-1.5 bg-slate-900 text-white rounded-lg text-xs font-semibold hover:bg-slate-800"
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
