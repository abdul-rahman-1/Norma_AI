import { Outlet, Navigate, Link } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import AIChatAssistant from '../components/AIChatAssistant';
import { Bell, Search, User, Compass, Sparkles, Command, Sun, Network, ShieldCheck, ChevronDown } from 'lucide-react';
import { motion, useScroll, useSpring } from 'framer-motion';
import { useState, useEffect } from 'react';

export default function Layout() {
  const token = localStorage.getItem('token');
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, { stiffness: 100, damping: 30, restDelta: 0.001 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => setMousePos({ x: e.clientX, y: e.clientY });
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  if (!token) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="flex h-screen bg-[#f8fafc] text-slate-900 font-display selection:bg-purple-100 selection:text-purple-600 overflow-hidden">
      {/* Interactive Background Neural Mesh */}
      <div 
        className="custom-glow" 
        style={{ left: mousePos.x, top: mousePos.y }}
      />
      
      <Sidebar />
      
      <div className="flex-1 flex flex-col relative overflow-hidden px-8 py-8 lg:px-12 lg:py-10">
        
        {/* State-of-the-Art Command Navbar */}
        <motion.header 
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="glass-luxury h-24 rounded-[3rem] flex items-center justify-between px-10 mb-10 z-50 relative group border border-white shadow-[0_20px_50px_-15px_rgba(0,0,0,0.03)]"
        >
          <div className="flex items-center gap-10 flex-1">
             {/* System Health Indicator */}
             <div className="flex items-center gap-4 bg-white/40 p-2.5 pr-6 rounded-2xl border border-white/50 shadow-inner group/node cursor-pointer hover:bg-white transition-all duration-500">
                <div className="w-10 h-10 rounded-xl bg-zinc-900 flex items-center justify-center text-emerald-400 shadow-xl group-hover/node:scale-110 transition-transform">
                   <Network size={18} className="animate-pulse" />
                </div>
                <div>
                   <p className="text-[9px] font-black text-slate-400 uppercase tracking-[0.4em] leading-none mb-1">Clinic Node</p>
                   <p className="text-xs font-black text-slate-800 uppercase tracking-tighter">Alpha-01 Online</p>
                </div>
             </div>
             
             <div className="h-10 w-[1px] bg-slate-100/50 hidden md:block" />
             
             {/* Global Command Search */}
             <div className="flex items-center gap-5 bg-slate-50/50 px-8 py-4 rounded-[1.8rem] border border-slate-100/50 focus-within:bg-white focus-within:shadow-[0_20px_40px_-10px_rgba(124,58,237,0.1)] focus-within:border-purple-200 transition-all duration-700 max-w-xl flex-1 group/search">
                <Search size={18} className="text-slate-300 group-focus-within/search:text-purple-500 transition-colors" />
                <input 
                  type="text" 
                  placeholder="Inquire about clinical data, patients, or schedules..." 
                  className="bg-transparent border-none outline-none text-sm w-full placeholder-slate-300 text-slate-600 font-bold tracking-tight"
                />
                <div className="hidden lg:flex items-center gap-2 px-2.5 py-1 bg-white rounded-lg border border-slate-100 text-[10px] font-black text-slate-300 uppercase tracking-widest">
                   <Command size={10} /> K
                </div>
             </div>
          </div>
          
          <div className="flex items-center gap-8 ml-8">
            {/* Utility Actions */}
            <div className="flex items-center gap-4">
              <div className="relative group/btn">
                <button className="nm-button-luxury w-12 h-12 rounded-xl flex items-center justify-center text-slate-400 hover:text-purple-600 transition-all duration-500">
                  <Bell size={20} />
                </button>
                <span className="absolute top-3 right-3 w-2 h-2 bg-purple-600 rounded-full border-2 border-white shadow-lg animate-pulse" />
              </div>
              <button className="nm-button-luxury w-12 h-12 rounded-xl flex items-center justify-center text-slate-400 hover:text-purple-600 transition-all duration-500">
                <Sun size={20} />
              </button>
            </div>
            
            <div className="h-10 w-[1px] bg-slate-100/50" />
            
            {/* Professional Identity Module */}
            <div className="flex items-center gap-5 pl-2 cursor-pointer group/profile relative">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-black text-slate-800 group-hover/profile:text-purple-600 transition-colors leading-none mb-1">Dr. Sarah Connor</p>
                <div className="flex items-center gap-2 justify-end">
                   <ShieldCheck size={10} className="text-purple-500" />
                   <p className="text-[9px] text-slate-400 font-black uppercase tracking-[0.2em]">Chief Medical Lead</p>
                </div>
              </div>
              <div className="w-14 h-14 rounded-[1.5rem] bg-zinc-900 border-4 border-white shadow-2xl overflow-hidden group-hover/profile:scale-105 group-hover/profile:shadow-purple-500/10 transition-all duration-500 relative">
                 <img src="https://i.pravatar.cc/100?u=sarah" alt="Profile" className="w-full h-full object-cover" />
                 <div className="absolute inset-0 bg-purple-600/10 opacity-0 group-hover/profile:opacity-100 transition-opacity" />
              </div>
              <ChevronDown size={14} className="text-slate-300 group-hover/profile:text-purple-500 transition-colors" />
            </div>
          </div>

          {/* SOTA Progress Ribbon */}
          <motion.div 
            className="absolute bottom-[-2px] left-0 right-0 h-1 bg-gradient-to-r from-purple-600 to-indigo-500 origin-left" 
            style={{ scaleX, borderRadius: '0 0 3rem 3rem' }} 
          />
        </motion.header>

        <main className="flex-1 overflow-y-auto pr-4 scrollbar-thin relative z-10 pb-32">
          <Outlet />
        </main>
      </div>

      <AIChatAssistant />
      
      {/* Background Aesthetic Orchestration */}
      <div className="fixed inset-0 pointer-events-none -z-20 mesh-bg opacity-40" />
    </div>
  );
}
