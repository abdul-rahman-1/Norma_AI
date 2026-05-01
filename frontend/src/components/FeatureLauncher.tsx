import React, { useState } from 'react';
import axios from 'axios';
import { Zap, Loader2, CheckCircle2, AlertCircle, ChevronRight, Bot, Sparkles } from 'lucide-react';
import { cn } from '../utils/cn';
import { motion, AnimatePresence } from 'framer-motion';

const FEATURES_LIST = [
  { id: 'B21_daily_briefing', name: 'Daily Briefing', role: 'STAFF', icon: Sparkles, desc: 'Morning clinical summary.' },
  { id: 'B24_bulk_shift', name: 'Bulk Shift', role: 'STAFF', icon: Zap, desc: 'Shift appointment blocks.' },
  { id: 'B27_waitlist_automation', name: 'Waitlist Sync', role: 'STAFF', icon: Bot, desc: 'Optimize slot vacancy.' },
];

export default function FeatureLauncher() {
  const [loading, setLoading] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const userRole = localStorage.getItem('role')?.toUpperCase() || 'PATIENT';

  const handleExecute = async (featureId: string) => {
    setLoading(featureId);
    setResult(null);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.post(`/api/features/execute/${featureId}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setResult({ status: 'success', data: res.data });
    } catch (err: any) {
      setResult({ status: 'error', message: err.response?.data?.detail || 'Execution failed.' });
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-8">
        <div>
           <h3 className="text-xl font-black text-white uppercase italic tracking-tight">Clinical Sentinel</h3>
           <p className="text-[10px] font-black text-[#44ddc1] uppercase tracking-[0.4em] mt-1">Direct Logic Execution</p>
        </div>
        <Bot size={24} className="text-[#44ddc1] animate-pulse" />
      </div>

      <div className="grid grid-cols-1 gap-4">
        {FEATURES_LIST.map((f) => {
          const isAllowed = f.role === 'PATIENT' || userRole === 'ADMIN' || userRole === 'DOCTOR' || userRole === 'STAFF';
          if (!isAllowed) return null;

          return (
            <button
              key={f.id}
              onClick={() => handleExecute(f.id)}
              disabled={!!loading}
              className="group flex items-center justify-between p-5 bg-[#131b2e] hover:bg-[#171f33] border border-transparent hover:border-[#44ddc1]/30 rounded-2xl transition-all text-left relative overflow-hidden"
            >
              <div className="flex items-center gap-5 relative z-10">
                <div className="w-12 h-12 rounded-xl bg-[#0b1326] flex items-center justify-center text-[#44ddc1] group-hover:scale-110 transition-transform shadow-xl">
                  {loading === f.id ? <Loader2 className="animate-spin" size={20} /> : <f.icon size={20} />}
                </div>
                <div>
                  <p className="text-sm font-black text-white uppercase tracking-tight">{f.name}</p>
                  <p className="text-[9px] font-bold text-[#85948f] uppercase tracking-widest mt-1">{f.desc}</p>
                </div>
              </div>
              <ChevronRight size={18} className="text-[#3c4a46] group-hover:text-[#44ddc1] group-hover:translate-x-1 transition-all" />
              
              {/* Active Glow */}
              <div className="absolute top-0 left-0 w-1 h-full bg-[#44ddc1] opacity-0 group-hover:opacity-100 transition-opacity" />
            </button>
          );
        })}
      </div>

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className={cn(
              "mt-8 p-6 rounded-2xl border flex items-start gap-4 shadow-2xl",
              result.status === 'success' ? "bg-[#44ddc1]/5 border-[#44ddc1]/20 text-[#44ddc1]" : "bg-red-500/5 border-red-500/20 text-red-400"
            )}
          >
            {result.status === 'success' ? <CheckCircle2 size={24} /> : <AlertCircle size={24} />}
            <div className="flex-1">
              <p className="text-[10px] font-black uppercase tracking-[0.2em] mb-2">{result.status === 'success' ? 'Execution Result' : 'System Diagnostic'}</p>
              <p className="text-sm font-bold leading-relaxed whitespace-pre-wrap">
                {result.status === 'success' ? JSON.stringify(result.data, null, 2) : result.message}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
