import React, { useState } from 'react';
import { parseFarmerRequest } from '../lib/api';
import { ParsedFarmerRequest } from '../lib/types';
import { MessageSquare, Sparkles, Send, CheckCircle, ArrowRight } from 'lucide-react';

const SAMPLE_MESSAGES = [
  "Mera naam Rameshwar Dass hai, Taraori se 5.5 kille dhaan ki straw padi hai. 2 din me clear karwa do bhai gehu bona hai.",
  "Gurpreet from Taraori GT Road, harvested 8 acres PR-126 today morning. Need baler before Thursday urgent.",
  "Jasbir from Pujam village, 12 acre ready by afternoon. Tractor trolley road clear, straw dry.",
  "Khanpur gaon se Virender, 8 acre ready tomorrow morning. Indri Bio plant is nearby.",
];

export const FarmerIntakeInbox: React.FC = () => {
  const [inputText, setInputText] = useState(SAMPLE_MESSAGES[0]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ParsedFarmerRequest | null>(null);

  const handleParse = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    try {
      const res = await parseFarmerRequest(inputText);
      setResult(res.extracted_data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-5 flex flex-col justify-between">
      {/* Header */}
      <div className="pb-3 border-b border-slate-100 mb-3 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <span>💬 AI Farmer Voice / SMS Intake Ingestion</span>
            <span className="text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 px-2 py-0.5 rounded-full">
              NLP Extractor
            </span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Parses noisy, multilingual, informal WhatsApp/voice transcriptions into verified harvest parameters.
          </p>
        </div>
      </div>

      {/* Preset Chips */}
      <div className="mb-3">
        <span className="text-[11px] font-semibold text-slate-500 block mb-1.5">
          Select sample farmer intake message:
        </span>
        <div className="flex flex-wrap gap-1.5">
          {SAMPLE_MESSAGES.map((msg, idx) => (
            <button
              key={idx}
              onClick={() => {
                setInputText(msg);
                setResult(null);
              }}
              className={`text-[11px] px-2.5 py-1 rounded-lg border text-left transition-colors truncate max-w-xs ${
                inputText === msg
                  ? 'bg-indigo-50 text-indigo-900 border-indigo-300 font-medium'
                  : 'bg-slate-50 hover:bg-slate-100 text-slate-600 border-slate-200'
              }`}
            >
              {msg}
            </button>
          ))}
        </div>
      </div>

      {/* Input Box */}
      <div className="relative mb-3">
        <textarea
          rows={3}
          value={inputText}
          onChange={e => setInputText(e.target.value)}
          placeholder="Paste colloquial Hindi/Hinglish/English farmer request..."
          className="w-full text-xs p-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 resize-none font-mono text-slate-800"
        />
        <button
          onClick={handleParse}
          disabled={loading || !inputText.trim()}
          className="absolute bottom-2.5 right-2.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white text-xs font-semibold rounded-lg shadow-sm flex items-center gap-1.5 disabled:opacity-50 transition-colors"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>{loading ? 'Extracting...' : 'Parse with AI'}</span>
        </button>
      </div>

      {/* Output Extraction Card */}
      {result ? (
        <div className="bg-slate-50 rounded-xl p-3.5 border border-indigo-100 animate-in fade-in">
          <div className="flex items-center justify-between pb-2 border-b border-slate-200/70 mb-2">
            <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
              Structured Farm Extraction Output
            </span>
            <span className="text-[10px] font-mono text-indigo-600 font-semibold bg-indigo-50 px-2 py-0.5 rounded">
              Ready for OR-Tools Formulation
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
            <div className="bg-white p-2 rounded-lg border border-slate-200">
              <span className="text-[10px] text-slate-400 block uppercase">Farmer</span>
              <span className="font-semibold text-slate-800 truncate block">{result.farmer_name}</span>
            </div>
            <div className="bg-white p-2 rounded-lg border border-slate-200">
              <span className="text-[10px] text-slate-400 block uppercase">Location</span>
              <span className="font-semibold text-slate-800 truncate block">{result.village} ({result.cluster})</span>
            </div>
            <div className="bg-white p-2 rounded-lg border border-slate-200">
              <span className="text-[10px] text-slate-400 block uppercase">Acreage & Straw</span>
              <span className="font-semibold text-slate-800 truncate block">{result.acres} ac (~{result.estimated_straw_tons} T)</span>
            </div>
            <div className="bg-white p-2 rounded-lg border border-slate-200">
              <span className="text-[10px] text-slate-400 block uppercase">Ready / Deadline</span>
              <span className="font-semibold text-slate-800 truncate block">H+{result.harvest_time_hours}h / H+{result.sowing_deadline_hours}h</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-4 bg-slate-50/60 rounded-xl border border-dashed border-slate-200 text-xs text-slate-400">
          Click "Parse with AI" to see real-time entity extraction from colloquial text.
        </div>
      )}
    </div>
  );
};
