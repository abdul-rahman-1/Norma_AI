import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Shield, Zap, MessageSquare, ChevronRight, Bot, Sparkles, ArrowRight, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';

const ScrambleText = ({ text }: { text: string }) => {
  const [display, setDisplay] = useState('');
  const chars = '!<>-_\\/[]{}—=+*^?#________';

  useEffect(() => {
    let iteration = 0;
    const interval = setInterval(() => {
      setDisplay(
        text.split('').map((char, index) => {
          if (index < iteration) return text[index];
          return chars[Math.floor(Math.random() * chars.length)];
        }).join('')
      );
      if (iteration >= text.length) clearInterval(interval);
      iteration += 1 / 3;
    }, 30);
    return () => clearInterval(interval);
  }, [text]);

  return <span>{display}</span>;
};

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white text-black overflow-x-hidden selection:bg-[#7c3aed]/20 selection:text-[#7c3aed] font-premium">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 w-full p-8 flex justify-between items-center z-[100] bg-white/80 backdrop-blur-xl border-b border-zinc-100">
        <div className="flex items-center gap-4">
          <div className="bg-black text-white p-2.5 rounded-xl shadow-2xl">
            <Activity size={24} />
          </div>
          <span className="text-2xl font-black tracking-tighter uppercase italic">Norma AI</span>
        </div>
        <div className="hidden md:flex items-center gap-12">
          {['Network', 'Sentinel', 'Infrastructure', 'Security'].map(item => (
            <a key={item} href="#" className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-400 hover:text-[#7c3aed] transition-all">{item}</a>
          ))}
        </div>
        <button 
          onClick={() => navigate('/login')}
          className="bg-black text-white px-8 py-3 rounded-xl font-black text-[10px] uppercase tracking-[0.2em] hover:bg-[#7c3aed] transition-all shadow-2xl flex items-center gap-3 active:scale-95"
        >
          Initialize Command <ArrowRight size={14} className="text-[#7c3aed]" />
        </button>
      </nav>

      {/* Hero Section */}
      <header className="relative pt-56 pb-40 px-10 flex flex-col items-center justify-center overflow-hidden">
        {/* Decorative Glows */}
        <div className="absolute top-40 left-1/2 -translate-x-1/2 w-[1200px] h-[700px] bg-[#7c3aed]/5 rounded-full blur-[140px] -z-10" />
        
        <motion.div 
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="max-w-6xl mx-auto text-center space-y-12 relative"
        >
          <div className="inline-flex items-center gap-3 px-5 py-2 rounded-xl bg-zinc-50 border border-zinc-200 mb-4 shadow-sm">
            <Sparkles size={16} className="text-[#7c3aed]" />
            <span className="text-[10px] font-black tracking-[0.4em] text-black uppercase leading-none">Clinical Sentinel v3.0.0</span>
          </div>
          
          <h1 className="text-8xl md:text-[150px] font-black tracking-tighter leading-[0.8] text-black uppercase italic">
            Clinical<br />
            <span className="text-[#7c3aed]">Sentinel</span>
          </h1>
          
          <p className="text-xl md:text-2xl text-zinc-500 max-w-3xl mx-auto font-medium leading-relaxed tracking-tight">
            High-fidelity clinical orchestration system. Automate patient flow, 
            synchronize diagnostic telemetry, and optimize practice efficiency via neural mesh.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-8 pt-10">
            <button 
              onClick={() => navigate('/login')}
              className="bg-black text-white px-12 py-7 rounded-xl font-black text-[12px] uppercase tracking-[0.3em] hover:bg-[#7c3aed] transition-all flex items-center gap-6 active:scale-95 shadow-2xl"
            >
              ESTABLISH UPLINK <ChevronRight size={20} className="text-[#7c3aed]" />
            </button>
            <button className="px-12 py-6 rounded-xl border-2 border-zinc-100 bg-white text-zinc-400 font-black tracking-[0.3em] text-[10px] hover:border-black hover:text-black transition-all flex items-center gap-4 shadow-sm">
              VIEW ARCHITECTURE <div className="w-2 h-2 rounded-full bg-black" />
            </button>
          </div>
        </motion.div>
      </header>

      {/* Feature Grid */}
      <section className="py-48 px-10 relative bg-zinc-50/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[
              { icon: Zap, title: "Neural Ingestion", desc: "Process complex clinical manifests and medical histories in milliseconds with zero error rate." },
              { icon: MessageSquare, title: "Clinical WhatsApp", desc: "Automate patient interaction via secure neural nodes with multi-turn memory integration." },
              { icon: Shield, title: "Identity Vault", desc: "Global patient identification with multi-layered role-based telemetry encryption." }
            ].map((f, i) => (
              <motion.div 
                key={i} 
                whileHover={{ y: -10 }}
                className="group space-y-10 p-12 rounded-[2.5rem] border border-zinc-200 bg-white hover:border-black transition-all duration-700 shadow-sm"
              >
                <div className="w-16 h-16 rounded-xl bg-black flex items-center justify-center text-white shadow-xl group-hover:bg-[#7c3aed] transition-all">
                  <f.icon size={32} />
                </div>
                <h3 className="text-3xl font-black tracking-tighter text-black uppercase italic">{f.title}</h3>
                <p className="text-zinc-500 font-medium leading-relaxed text-lg">{f.desc}</p>
                <div className="pt-4 flex items-center gap-3 text-black text-[10px] font-black uppercase tracking-[0.3em] opacity-40 group-hover:opacity-100 transition-opacity">
                   <span>Secure Protocol</span>
                   <ArrowRight size={14} className="text-[#7c3aed]" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Infrastructure Node Section */}
      <section className="py-48 px-10 bg-white">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-32 items-center">
          <div className="space-y-12">
            <div className="space-y-4">
              <h2 className="text-6xl md:text-8xl font-black tracking-tighter leading-[0.85] text-black uppercase italic">
                Robust<br />
                <span className="text-[#7c3aed]">Mesh</span>
              </h2>
              <p className="text-xl text-zinc-500 font-medium leading-relaxed max-w-xl">
                Distributed clinical network architecture designed for 99.99% uptime and sub-10ms global synchronization.
              </p>
            </div>
            <div className="space-y-6">
              {[
                "Distributed Database Multi-Node Sync",
                "Real-time AI Clinical Telemetry",
                "Automated Registry Identity Provisioning",
                "High-Availability Cloud Edge Orchestration"
              ].map((item, i) => (
                <motion.div key={i} whileHover={{ x: 10 }} className="flex items-center gap-6 group">
                  <div className="w-8 h-8 rounded-lg bg-black/5 flex items-center justify-center text-black border border-zinc-100 group-hover:bg-black group-hover:text-white transition-all">
                    <CheckCircle2 size={18} />
                  </div>
                  <span className="font-black text-lg text-black tracking-tight uppercase italic">{item}</span>
                </motion.div>
              ))}
            </div>
          </div>
          
          <div className="relative group">
            <div className="absolute inset-0 bg-[#7c3aed]/5 rounded-[3rem] rotate-3 -z-10 blur-2xl opacity-0 group-hover:opacity-100 transition-all duration-1000" />
            <div className="bg-black p-12 rounded-[3rem] shadow-2xl border border-zinc-800 relative overflow-hidden">
              <div className="flex items-center justify-between mb-12">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-white/20" />
                  <div className="w-3 h-3 rounded-full bg-white/20" />
                  <div className="w-3 h-3 rounded-full bg-[#7c3aed]/50 shadow-[0_0_8px_rgba(124,58,237,0.5)]" />
                </div>
                <div className="text-[10px] font-black text-zinc-600 uppercase tracking-[0.5em] italic">Mesh_Terminal_v3.0.log</div>
              </div>
              <div className="space-y-6 font-mono text-sm leading-relaxed text-zinc-400">
                <p className="text-[#7c3aed] font-bold underline mb-6 tracking-widest"><ScrambleText text="INITIALIZE_SENTINEL_UPLINK..." /></p>
                <p><span className="text-[#7c3aed]">[OK]</span> CLINICAL_DB_MESH CONNECTED</p>
                <p><span className="text-[#7c3aed]">[OK]</span> NEURAL_SENTINEL_NODE ACTIVE</p>
                <p><span className="text-[#7c3aed]">[OK]</span> WHATSAPP_BRIDGE SECURED</p>
                <p className="text-white animate-pulse"><span className="text-[#7c3aed]">[&gt;]</span> SYNCING REGISTRY TELEMETRY...</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-24 px-10 border-t border-zinc-100 bg-white">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-12">
          <div className="flex items-center gap-4">
            <div className="bg-black text-white p-2 rounded-lg">
              <Activity size={24} />
            </div>
            <span className="text-2xl font-black tracking-tighter uppercase italic">Norma AI</span>
          </div>
          <p className="text-[11px] font-black text-zinc-400 tracking-[0.4em] uppercase text-center">
            &copy; 2026 NORMA AI CLINICAL SYSTEMS • HIGH-FIDELITY MEDICAL ORCHESTRATION
          </p>
          <div className="flex gap-10">
            {['Privacy', 'Network', 'Uptime'].map(item => (
              <a key={item} href="#" className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-400 hover:text-[#7c3aed] transition-all">{item}</a>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}
