import React, { useState } from 'react';
import { SimulationState, Farm, Baler, Buyer } from '../lib/types';
import { MapPin, Navigation, Info } from 'lucide-react';

interface FarmMapProps {
  state: SimulationState | null;
}

export const FarmMap: React.FC<FarmMapProps> = ({ state }) => {
  const [hoveredNode, setHoveredNode] = useState<{ title: string; subtitle: string; details: string } | null>(null);

  const farms = state?.farms || [];
  const balers = state?.balers || [];
  const buyers = state?.buyers || [];
  const jobs = state?.current_plan?.jobs || [];

  // Coordinate bounding box for Karnal district mapping
  // Lat: 29.50 to 29.95 | Lng: 76.85 to 77.15
  const minLat = 29.50;
  const maxLat = 29.93;
  const minLng = 76.85;
  const maxLng = 77.12;

  const project = (lat: number, lng: number) => {
    const x = ((lng - minLng) / (maxLng - minLng)) * 740 + 30;
    const y = ((maxLat - lat) / (maxLat - minLat)) * 340 + 30; // invert latitude for SVG
    return { x: Math.max(20, Math.min(780, x)), y: Math.max(20, Math.min(380, y)) };
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-5 flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
        <div>
          <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <span>🗺️ Karnal Agro-Logistics Cluster Map</span>
            <span className="text-[10px] font-mono bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200">
              15 Farms • 3 Balers • 4 Off-Takers
            </span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Geographic dispersion across Taraori, Nilokheri, Indri, and Karnal Central agricultural belts.
          </p>
        </div>

        {/* Dynamic Hover Tooltip info */}
        {hoveredNode ? (
          <div className="text-xs bg-slate-900 text-white px-3 py-1.5 rounded-lg shadow-md max-w-xs animate-in fade-in">
            <div className="font-bold">{hoveredNode.title}</div>
            <div className="text-[11px] text-slate-300">{hoveredNode.subtitle}</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">{hoveredNode.details}</div>
          </div>
        ) : (
          <div className="text-xs text-slate-400 flex items-center gap-1">
            <Info className="w-3.5 h-3.5" />
            <span>Hover on node for live routing</span>
          </div>
        )}
      </div>

      {/* SVG Canvas Map */}
      <div className="relative w-full h-[360px] bg-slate-50/70 rounded-xl border border-slate-200 overflow-hidden flex items-center justify-center">
        {/* District Cluster Labels */}
        <div className="absolute top-4 left-6 text-xs font-bold text-slate-400 uppercase tracking-wider select-none">
          Nilokheri Cluster (North)
        </div>
        <div className="absolute top-12 left-1/4 text-xs font-bold text-slate-400 uppercase tracking-wider select-none">
          Taraori Basmati Zone
        </div>
        <div className="absolute top-4 right-8 text-xs font-bold text-slate-400 uppercase tracking-wider select-none">
          Indri Bio-Hub (East)
        </div>
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-xs font-bold text-slate-400 uppercase tracking-wider select-none">
          Karnal Central / South Highway
        </div>

        <svg viewBox="0 0 800 400" className="w-full h-full">
          {/* Subtle connecting lines from farms to buyers based on active jobs */}
          {jobs.map(job => {
            const farm = farms.find(f => f.id === job.farm_id);
            const buyer = buyers.find(b => b.id === job.buyer_id);
            if (!farm || !buyer) return null;

            const fp = project(farm.location.lat, farm.location.lng);
            const bp = project(buyer.location.lat, buyer.location.lng);

            return (
              <line
                key={`route-${job.id}`}
                x1={fp.x}
                y1={fp.y}
                x2={bp.x}
                y2={bp.y}
                stroke={job.status === 'disrupted' ? '#ef4444' : '#10b981'}
                strokeWidth={job.status === 'disrupted' ? 1.5 : 1}
                strokeDasharray={job.status === 'disrupted' ? '4 4' : 'none'}
                opacity={0.35}
              />
            );
          })}

          {/* Buyer Hub Nodes */}
          {buyers.map(b => {
            const pt = project(b.location.lat, b.location.lng);
            return (
              <g
                key={b.id}
                transform={`translate(${pt.x}, ${pt.y})`}
                className="cursor-pointer"
                onMouseEnter={() => setHoveredNode({
                  title: b.name,
                  subtitle: `Off-Taker Type: ${b.buyer_type.replace('_', ' ').toUpperCase()}`,
                  details: `Daily Capacity: ${b.daily_intake_capacity_tons} Tons | Rate: ₹${b.price_per_ton}/ton`
                })}
                onMouseLeave={() => setHoveredNode(null)}
              >
                <circle r={14} fill="#0284c7" opacity={0.2} />
                <rect x={-8} y={-8} width={16} height={16} rx={4} fill="#0284c7" stroke="#ffffff" strokeWidth={2} />
                <text x={0} y={18} textAnchor="middle" fontSize={10} fontWeight="bold" fill="#0f172a">
                  {b.name.split(' ')[0]}
                </text>
              </g>
            );
          })}

          {/* Baler Depot Nodes */}
          {balers.map(baler => {
            const pt = project(baler.depot_location.lat, baler.depot_location.lng);
            const isBroken = baler.status === 'broken_down';
            return (
              <g
                key={baler.id}
                transform={`translate(${pt.x}, ${pt.y})`}
                className="cursor-pointer"
                onMouseEnter={() => setHoveredNode({
                  title: `${baler.id.toUpperCase()}: ${baler.operator_name}`,
                  subtitle: `Status: ${baler.status.toUpperCase()} (${baler.baler_type})`,
                  details: `Capacity: ${baler.throughput_acres_per_hour} ac/hr • Depot Location`
                })}
                onMouseLeave={() => setHoveredNode(null)}
              >
                <circle r={isBroken ? 16 : 14} fill={isBroken ? '#ef4444' : '#f59e0b'} opacity={isBroken ? 0.35 : 0.25} />
                <polygon points="0,-10 9,6 -9,6" fill={isBroken ? '#ef4444' : '#f59e0b'} stroke="#ffffff" strokeWidth={1.5} />
                <text x={0} y={20} textAnchor="middle" fontSize={10} fontWeight="bold" fill={isBroken ? '#b91c1c' : '#78350f'}>
                  {baler.id.toUpperCase()} {isBroken ? '⚠️' : ''}
                </text>
              </g>
            );
          })}

          {/* Farm Nodes */}
          {farms.map(farm => {
            const pt = project(farm.location.lat, farm.location.lng);
            const job = jobs.find(j => j.farm_id === farm.id);
            const isDisrupted = job?.status === 'disrupted';
            const isScheduled = Boolean(job);

            let nodeColor = '#94a3b8'; // pending gray
            if (isDisrupted) nodeColor = '#ef4444'; // red
            else if (isScheduled) nodeColor = '#10b981'; // green

            return (
              <g
                key={farm.id}
                transform={`translate(${pt.x}, ${pt.y})`}
                className="cursor-pointer transition-transform hover:scale-125"
                onMouseEnter={() => setHoveredNode({
                  title: `${farm.farmer_name} (${farm.acres} acres)`,
                  subtitle: `${farm.village} • Harvest Ready: ${farm.harvest_time_hours}h • Sowing Deadline: ${farm.sowing_deadline_hours}h`,
                  details: job ? `Assigned to ${job.baler_id.toUpperCase()} (Start: hour ${job.start_hour})` : 'Status: Pending Assignment'
                })}
                onMouseLeave={() => setHoveredNode(null)}
              >
                <circle r={7} fill={nodeColor} stroke="#ffffff" strokeWidth={1.5} />
                <text x={0} y={-10} textAnchor="middle" fontSize={9} fill="#475569" fontWeight="600">
                  {farm.farmer_name.split(' ')[0]}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend Footer */}
      <div className="mt-3 pt-2 border-t border-slate-100 flex flex-wrap items-center justify-between text-[11px] text-slate-500">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
            <span>Farm (Cleared / Scheduled)</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block animate-pulse" />
            <span>Disrupted Farm</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-amber-500 inline-block" />
            <span>Baler Depot</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-sky-600 inline-block" />
            <span>Industrial Buyer Off-Taker</span>
          </span>
        </div>
        <span className="font-mono text-slate-400">Map Scale: ~35 km diameter</span>
      </div>
    </div>
  );
};
