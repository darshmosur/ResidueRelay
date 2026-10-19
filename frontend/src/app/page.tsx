'use client';

import React, { useEffect, useState } from 'react';
import { SimulationState } from '../lib/types';
import {
  fetchState,
  resetSimulation,
  generateInitialSchedule,
  triggerDisruption,
  replanSchedule,
  approvePlan,
} from '../lib/api';
import { Header } from '../components/Header';
import { MetricsStrip } from '../components/MetricsStrip';
import { DisruptionSimulator } from '../components/DisruptionSimulator';
import { TimelineGantt } from '../components/TimelineGantt';
import { PlanDiffModal } from '../components/PlanDiffModal';
import { FarmMap } from '../components/FarmMap';
import { FarmerIntakeInbox } from '../components/FarmerIntakeInbox';

export default function DashboardPage() {
  const [state, setState] = useState<SimulationState | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadState = async () => {
    try {
      setError(null);
      const data = await fetchState();
      setState(data);
    } catch (err: any) {
      console.error(err);
      setError('Unable to connect to ResidueRelay backend. Please ensure FastAPI server is running on port 8000.');
    }
  };

  useEffect(() => {
    loadState();
  }, []);

  const handleReset = async () => {
    setLoading(true);
    try {
      const data = await resetSimulation();
      setState(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      await generateInitialSchedule();
      await loadState();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDisrupt = async (preset: 'rain' | 'breakdown' | 'both') => {
    setLoading(true);
    try {
      const data = await triggerDisruption(preset);
      setState(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReplan = async () => {
    setLoading(true);
    try {
      await replanSchedule();
      await loadState();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    setLoading(true);
    try {
      await approvePlan();
      await loadState();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Header */}
      <Header state={state} onReset={handleReset} loading={loading} />

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6 grow w-full">
        {/* Error notification banner */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-xl text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="font-bold">Backend Communication Notice:</span>
              <span>{error}</span>
            </div>
            <button
              onClick={loadState}
              className="px-3 py-1 bg-red-600 text-white rounded-lg text-[11px] font-semibold hover:bg-red-700"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* 1. Operational Key Performance Metrics */}
        <MetricsStrip state={state} />

        {/* 2. Interactive Disruption Simulator Deck */}
        <DisruptionSimulator
          state={state}
          loading={loading}
          onGenerate={handleGenerate}
          onDisrupt={handleDisrupt}
          onReplan={handleReplan}
          onApprove={handleApprove}
        />

        {/* 3. Human-in-the-Loop Approval & Plan Comparison Banner */}
        <PlanDiffModal
          state={state}
          onApprove={handleApprove}
          loading={loading}
        />

        {/* 4. Fleet Timeline & Baler Utilization (Gantt View) */}
        <TimelineGantt state={state} />

        {/* 5. Geographic Cluster Map & AI Intake Ingestion Split Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <FarmMap state={state} />
          <FarmerIntakeInbox />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-500">
          <div>
            <span className="font-semibold text-slate-700">ResidueRelay</span> • Synchronized Harvest & Crop Residue Logistics System
          </div>
          <div className="flex items-center gap-3">
            <span>Google OR-Tools CP-SAT</span>
            <span>•</span>
            <span>FastAPI Backend</span>
            <span>•</span>
            <span>Next.js 14 Dashboard</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
