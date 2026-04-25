import { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, Users, Building2, Activity, Database, Key, 
  AlertTriangle, Server, ChevronRight, Search, Cpu, 
  Zap, Globe, ShieldCheck, HardDrive, RefreshCw, 
  Terminal, Lock, Fingerprint, Network, MoreVertical,
  ShieldAlert, CheckCircle2, CloudLightning, Cpu as Brain
} from 'lucide-react';
import { cn } from '../utils/cn';

const containerVariants: any = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1, 
    transition: { staggerChildren: 0.1, delayChildren: 0.2 } 
  }
};

const itemVariants: any = {
  hidden: { y: 20, opacity: 0 },
  visible: { 
    y: 0, 
    opacity: 1, 
    transition: { type: "spring", stiffness: 100, damping: 15 } 
  }
};

export default function AdminDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

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
    { label: 'Network Latency', value: '14ms', status: 'Optimal', icon: Globe, color: 'text-emerald-500' },
    { label: 'Mesh Integrity', value: '99.9%', status: 'Synced', icon: Database, color: 'text-purple-600' },
    { label: 'Sentinel Core', value: 'Active', status: 'Protocol 2.5', icon: Brain, color: 'text-blue-500' },
    { label: 'Quantum Shield', value: 'Secured', status: 'AES-512', icon: ShieldCheck, color: 'text-indigo-600' },
  ];

  if (loading) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-[#f8fafc]">
        <motion.div animate={{ scale: [0.9, 1.1, 0.9], opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 3 }} className="nm-luxury p-20 rounded-full relative">
           <div className="absolute inset-0 blur-3xl bg-purple-500/10 rounded-full" />
           <Server className="text-purple-600 relative z-10" size={64} />
        </motion.div>
        <p className="mt-12 text-[10px] font-black uppercase tracking-[0.5em] text-slate-400 animate-pulse">Establishing Root Uplink</p>
      </div>
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto space-y-12 animate-in fade-in duration-1000 pb-20">
      {/* Admin Header */}
      <header className="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-10">
        <div className="space-y-4">
          <div className="inline-flex items-center gap-3 px-4 py-2 rounded-2xl bg-purple-50 border border-purple-100">
             <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)] animate-pulse" />
             <span className="text-[10px] font-black text-purple-600 uppercase tracking-[0.4em]">Root Administrator Authorized</span>
          </div>
          <h1 className="text-6xl font-black text-slate-900 tracking-tighter uppercase italic leading-none">System Control</h1>
          <p className="text-slate-400 font-medium text-xl italic max-w-2xl leading-relaxed">High-fidelity orchestration of clinical neural nodes and distributed infrastructure.</p>
        </div>
        
        <div className="flex gap-6">
           <button className="nm-button-luxury px-12 py-6 rounded-[2rem] text-[10px] font-black uppercase tracking-[0.3em] text-slate-600 flex items-center gap-4 hover:text-purple-600">
              <RefreshCw size={18} className="text-purple-600" />
              Reset Nodes
           </button>
           <button className="bg-zinc-900 text-white px-12 py-6 rounded-[2rem] text-[10px] font-black uppercase tracking-[0.3em] shadow-2xl shadow-zinc-900/20 hover:bg-purple-600 transition-all flex items-center gap-5">
              <Terminal size={18} className="text-purple-400" />
              System Console
           </button>
        </div>
      </header>

      {/* SOTA Metrics Row */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10">
        {systemMetrics.map((m, i) => (
          <motion.div 
            key={i}
            whileHover={{ y: -5 }}
            className="nm-luxury p-10 rounded-[3.5rem] border border-white relative overflow-hidden group cursor-default"
          >
            <div className="flex justify-between items-start mb-12">
              <div className={cn("p-5 rounded-2xl bg-slate-50 border border-white shadow-inner transition-transform group-hover:scale-110 duration-700", m.color)}>
                 <m.icon size={30} />
              </div>
              <div className="flex flex-col items-end">
                 <span className="text-[10px] font-black text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-xl uppercase tracking-widest">{m.status}</span>
                 <p className="text-[9px] font-black text-slate-300 uppercase tracking-widest mt-3">Metric v2.5</p>
              </div>
            </div>
            <div>
              <p className="text-[11px] font-black text-slate-400 uppercase tracking-[0.4em] mb-3">{m.label}</p>
              <p className="text-5xl font-black text-slate-900 tracking-tighter italic">{m.value}</p>
            </div>
            <div className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-purple-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          </motion.div>
        ))}
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
        {/* Network Infrastructure Node Map */}
        <div className="lg:col-span-8 space-y-12">
           <div className="nm-luxury p-12 rounded-[4rem] border border-white relative overflow-hidden bg-white/40 glass">
              <div className="flex flex-col md:flex-row md:items-center justify-between mb-16 gap-10">
                 <div className="flex items-center gap-8">
                    <div className="w-16 h-16 rounded-[2rem] bg-zinc-900 flex items-center justify-center text-purple-400 shadow-2xl">
                       <Network size={32} />
                    </div>
                    <div>
                       <h2 className="text-3xl font-black text-slate-900 tracking-tighter uppercase leading-none italic">Distributed Nodes</h2>
                       <p className="text-[10px] text-gray-400 font-black uppercase tracking-[0.4em] mt-3 italic">Clinical Ingestion Mesh Alpha</p>
                    </div>
                 </div>
                 <div className="flex p-2 bg-slate-50 rounded-[2rem] gap-1 shadow-inner border border-white">
                    {['Active', 'Offline', 'History'].map(tab => (
                      <button key={tab} className={cn("px-10 py-4 rounded-[1.5rem] text-[10px] font-black uppercase tracking-[0.3em] transition-all duration-500", tab === 'Active' ? "bg-white text-slate-900 shadow-xl border border-slate-100" : "text-slate-400 hover:text-slate-600")}>
                        {tab}
                      </button>
                    ))}
                 </div>
              </div>
              
              <div className="space-y-8">
                {[
                  { name: 'Core Sentinel (Primary)', location: 'Cloud Mesh', load: '12%', status: 'Optimal', icon: Brain },
                  { name: 'Identity Resolver (Edge)', location: 'Secure Node DX-2', load: '45%', status: 'Thinking', icon: Fingerprint },
                  { name: 'Global Database Cluster', location: 'Distributed M-8', load: '8%', status: 'Synced', icon: HardDrive },
                  { name: 'Omnichannel Webhook', location: 'Secure Tunnel', load: '22%', status: 'Listening', icon: Zap },
                ].map((node, i) => (
                  <motion.div key={i} whileHover={{ x: 10 }} className="flex items-center justify-between p-10 rounded-[3rem] bg-slate-50/50 border border-white hover:bg-white hover:shadow-2xl transition-all duration-700 group cursor-default">
                    <div className="flex items-center gap-8">
                       <div className="w-16 h-16 rounded-[1.5rem] nm-inset bg-white flex items-center justify-center text-purple-600 group-hover:scale-110 transition-transform duration-700">
                          <node.icon size={26} />
                       </div>
                       <div>
                          <p className="text-xl font-black text-slate-900 tracking-tighter uppercase italic">{node.name}</p>
                          <p className="text-[11px] font-black text-slate-400 uppercase tracking-widest mt-2 opacity-60">{node.location}</p>
                       </div>
                    </div>
                    <div className="flex items-center gap-16">
                       <div className="text-right">
                          <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest mb-2">Pressure Vector</p>
                          <p className="text-lg font-black text-slate-600 italic">{node.load}</p>
                       </div>
                       <div className={cn("px-6 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest border-2", node.status === 'Optimal' ? 'bg-emerald-50 border-emerald-100 text-emerald-600' : 'bg-purple-50 border-purple-100 text-purple-600 animate-pulse')}>
                          {node.status}
                       </div>
                       <button className="nm-button-luxury p-4 rounded-2xl text-slate-300 hover:text-purple-600 transition-all">
                          <MoreVertical size={24} />
                       </button>
                    </div>
                  </motion.div>
                ))}
              </div>
           </div>
        </div>

        {/* Security Matrix Panel */}
        <div className="lg:col-span-4 space-y-12">
           <motion.div variants={itemVariants} className="nm-luxury p-12 rounded-[4rem] border border-white relative overflow-hidden group bg-zinc-900 text-white">
              <div className="absolute top-0 right-0 p-12 opacity-10 group-hover:rotate-45 transition-transform duration-1000">
                 <Shield size={180} className="text-purple-500" />
              </div>
              <h2 className="text-2xl font-black tracking-tighter uppercase mb-16 flex items-center gap-5 italic leading-none relative z-10">
                 <Lock size={28} className="text-purple-500 shadow-2xl" />
                 Security Hub
              </h2>
              
              <div className="space-y-12 relative z-10">
                 {[
                   { label: 'Role Authority', detail: 'RBAC Enabled v2', icon: Users, color: 'text-blue-400' },
                   { label: 'Digital Fingerprint', detail: 'E2EE Ingestion', icon: Fingerprint, color: 'text-purple-400' },
                   { label: 'Encryption Node', detail: 'Root Rotated 4h ago', icon: Key, color: 'text-emerald-400' },
                 ].map((item, i) => (
                   <div key={i} className="flex gap-8 group/item hover:translate-x-2 transition-transform duration-700">
                      <div className="w-16 h-16 rounded-[1.5rem] bg-white/5 border border-white/5 flex items-center justify-center text-slate-500 group-hover/item:text-white transition-colors duration-500">
                         <item.icon size={26} className={item.color} />
                      </div>
                      <div className="pt-2">
                         <p className="text-[10px] font-black text-gray-500 uppercase tracking-[0.3em] mb-2">{item.label}</p>
                         <p className="text-base font-black tracking-tight italic opacity-90">{item.detail}</p>
                      </div>
                   </div>
                 ))}
              </div>
              
              <button className="w-full mt-20 py-7 rounded-[2rem] bg-white text-zinc-900 text-[10px] font-black uppercase tracking-[0.4em] hover:bg-purple-600 hover:text-white transition-all duration-700 shadow-2xl relative z-10">
                 Full Security Audit
              </button>
           </motion.div>

           {/* Institutional Compliance Node */}
           <motion.div variants={itemVariants} className="glass-luxury p-12 rounded-[4rem] border border-white shadow-2xl relative overflow-hidden text-center group bg-white/40">
              <div className="mx-auto w-24 h-24 rounded-[2rem] bg-purple-600 flex items-center justify-center text-white shadow-2xl shadow-purple-600/30 mb-10 group-hover:rotate-12 transition-transform duration-1000">
                 <ShieldCheck size={48} />
              </div>
              <h3 className="text-3xl font-black text-slate-900 uppercase tracking-tighter mb-5 italic">Institutional Rank</h3>
              <p className="text-base text-slate-500 font-medium leading-relaxed italic mb-12 px-6">"Norma AI exceeds clinical data safety standards in the current session cycle."</p>
              <div className="flex flex-wrap justify-center gap-6 text-[10px] font-black text-slate-400 uppercase tracking-[0.4em]">
                 <span className="flex items-center gap-2.5 px-4 py-2 bg-emerald-50 rounded-xl text-emerald-600"><CheckCircle2 size={14} /> HIPAA</span>
                 <span className="flex items-center gap-2.5 px-4 py-2 bg-emerald-50 rounded-xl text-emerald-600"><CheckCircle2 size={14} /> GDPR</span>
                 <span className="flex items-center gap-2.5 px-4 py-2 bg-emerald-50 rounded-xl text-emerald-600"><CheckCircle2 size={14} /> HL7-v2</span>
              </div>
           </motion.div>
        </div>
      </div>
    </div>
  );
}
