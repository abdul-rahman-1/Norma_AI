import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { Search, Bell, Sun, Command } from 'lucide-react';

export default function Layout() {
  return (
    <div className="flex h-screen bg-[#f8fafc] overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navigation Mesh from Image */}
        <header className="h-32 flex items-center justify-between px-12 z-10">
          <div className="flex items-center gap-12">
            <div className="nm-flat px-8 py-4 rounded-2xl flex items-center gap-4 border border-white/50">
               <div className="w-10 h-10 rounded-xl bg-zinc-900 flex items-center justify-center text-white shadow-lg">
                  <Command size={20} />
               </div>
               <div>
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest leading-none">Navigation Mesh</p>
                  <p className="text-sm font-black text-slate-800 uppercase tracking-tighter mt-1">Clinical Hub V2.5</p>
               </div>
            </div>

            <div className="nm-inset w-[500px] px-8 py-4 rounded-2xl flex items-center gap-4 border border-white/40">
               <Search size={18} className="text-slate-300" />
               <input type="text" placeholder="Ask for any patient or medical record..." className="bg-transparent border-none outline-none text-sm w-full font-bold text-slate-800 placeholder-slate-300" />
            </div>
          </div>

          <div className="flex items-center gap-8">
            <div className="flex items-center gap-4">
               <button className="nm-button w-12 h-12 rounded-2xl flex items-center justify-center text-slate-400 hover:text-violet-600 transition-all">
                  <Bell size={20} />
               </button>
               <button className="nm-button w-12 h-12 rounded-2xl flex items-center justify-center text-slate-400 hover:text-violet-600 transition-all">
                  <Sun size={20} />
               </button>
            </div>

            <div className="flex items-center gap-6 pl-8 border-l border-slate-100">
               <div className="text-right">
                  <p className="text-sm font-black text-slate-800 leading-none">Dr. Sarah Connor</p>
                  <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mt-1.5">Lead Consultant</p>
               </div>
               <div className="w-14 h-14 rounded-2xl border-4 border-white shadow-2xl overflow-hidden nm-flat">
                  <img src="https://i.pravatar.cc/150?u=sarah" alt="Profile" className="w-full h-full object-cover" />
               </div>
            </div>
          </div>
        </header>

        {/* Purple separator line from image */}
        <div className="mx-12 h-[2px] bg-gradient-to-r from-violet-600 via-violet-400 to-transparent opacity-30 mb-8" />

        <main className="flex-1 overflow-y-auto px-12 scrollbar-thin">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
