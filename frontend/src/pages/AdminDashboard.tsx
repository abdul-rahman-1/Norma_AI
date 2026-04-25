import { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, Globe, Database, Cpu, Lock, 
  RefreshCw, Terminal, Activity, MoreVertical,
  CheckCircle2, Sparkles, Send, Loader2
} from 'lucide-react';
import { cn } from '../utils/cn';

export default function AdminDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(null), 3000);
  };

  useEffect(() => {
    const fetchAdminStats = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await axios.get('http://localhost:5000/api/dashboard/stats', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setStats(res.data);
      } catch (err) {
        console.error('Admin telemetry sync failed', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAdminStats();
  }, []);

  const systemMetrics = [
    { label: 'Cloud Latency', value: '14ms', status: 'Optimal', icon: Globe, color: 'text-emerald-500' },
    { label: 'Database Health', value: '99.9%', status: 'Synced', icon: Database, color: 'text-violet-600' },
    { label: 'Neural Engine', value: 'Active', status: 'Protocol 2.5', icon: Cpu, color: 'text-blue-500' },
    { label: 'Security Mesh', value: 'Encrypted', status: 'AES-256', icon: Shield, color: 'text-violet-600' },
  ];

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="animate-spin text-violet-600" size={48} />
      </div>
    );
  }

  return (
    <div className="max-w-[1400px] mx-auto space-y-16 animate-in fade-in duration-1000 pb-20 relative">
      
      <AnimatePresence>
        {toast && (
          <motion.div 
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-10 left-1/2 -translate-x-1/2 z-50 bg-slate-900 text-white px-10 py-5 rounded-full flex items-center gap-3 shadow-2xl font-black uppercase tracking-widest text-[10px]"
          >
            <Activity size={20} className="text-violet-400" />
            {toast}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Admin Header from Image */}
      <header className="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-8 pt-8">
        <div className="space-y-4">
          <div className="flex items-center gap-3">
             <div className="w-3 h-3 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_12px_rgba(16,185,129,0.5)]" />
             <span className="text-[11px] font-black text-slate-400 uppercase tracking-[0.4em]">System Administrator Privileges Active</span>
          </div>
          <h1 className="text-7xl font-black text-slate-900 tracking-tighter uppercase italic leading-none">System Control</h1>
          <p className="text-slate-500 font-bold text-xl italic opacity-80">Master orchestration of the clinical network and neural nodes.</p>
        </div>
        
        <div className="flex items-center gap-12">
           <button onClick={() => showToast('Command: Reboot Nodes Executed')} className="flex items-center gap-4 text-[11px] font-black text-slate-400 uppercase tracking-[0.4em] hover:text-violet-600 transition-colors group">
              <RefreshCw size={20} className="text-violet-600 group-hover:rotate-180 transition-transform duration-700" />
              Reboot Nodes
           </button>
           <button className="bg-[#0b1326] text-white px-16 py-7 rounded-[1.8rem] text-[12px] font-black uppercase tracking-[0.4em] shadow-2xl shadow-slate-900/20 hover:bg-violet-600 transition-all active:scale-95 flex items-center gap-6">
              <Send size={20} className="text-violet-400" />
              Open Console
           </button>
        </div>
      </header>

      {/* SOTA Metrics Row - Exact Image Style */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
        {systemMetrics.map((m, i) => (
          <div 
            key={i}
            className="nm-luxury p-12 aspect-square flex flex-col justify-between relative overflow-hidden group border-4 border-white/50"
          >
            <div className="flex justify-between items-start">
              <div className="w-20 h-20 rounded-[2rem] bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-300 transition-all group-hover:bg-white group-hover:shadow-lg group-hover:text-violet-600">
                 <m.icon size={36} className={m.color} />
              </div>
              <span className={cn("px-5 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest", 
                m.status === 'Optimal' || m.status === 'Synced' ? 'bg-emerald-50 text-emerald-500' : 'bg-violet-50 text-violet-600')}>
                {m.status}
              </span>
            </div>
            
            <div className="space-y-4">
              <p className="text-[12px] font-black text-slate-400 uppercase tracking-[0.4em]">{m.label}</p>
              <p className="text-6xl font-black text-slate-900 tracking-tighter leading-none">{m.value}</p>
            </div>
          </div>
        ))}
      </section>

      {/* Bottom Node Bar from Image */}
      <div className="nm-flat p-4 rounded-full border border-white flex items-center justify-between px-12 bg-white/80 backdrop-blur-md">
         <div className="flex items-center gap-4">
            <div className="w-3 h-3 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.5)]" />
            <span className="text-[11px] font-black text-slate-400 uppercase tracking-[0.3em]">Node Alpha Online</span>
         </div>
         
         <div className="flex items-center gap-16">
            {['Diagnostics', 'Encounters', 'Global Registry'].map(item => (
              <button key={item} className="text-[11px] font-black text-slate-400 uppercase tracking-[0.4em] hover:text-violet-600 transition-colors">
                {item}
              </button>
            ))}
         </div>
      </div>

      {/* Floating Chat Icon from Image */}
      <div className="fixed bottom-12 right-12 z-[100]">
         <div className="relative group">
            <button className="w-20 h-20 rounded-[1.8rem] bg-violet-600 text-white flex items-center justify-center shadow-2xl shadow-violet-500/40 hover:scale-110 transition-all active:scale-95">
               <MessageSquare size={32} />
            </button>
            <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full border-4 border-white animate-pulse" />
         </div>
      </div>
    </div>
  );
}

function MessageSquare({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
    </svg>
  );
}
