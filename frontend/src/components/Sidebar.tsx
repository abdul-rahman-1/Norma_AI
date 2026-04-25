import { Link, useLocation } from 'react-router-dom';
import { Home, Calendar, Users, UploadCloud, Settings, LogOut, Shield, Heart, Info, MessageSquare, Stethoscope } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Sidebar() {
  const location = useLocation();
  const role = localStorage.getItem('role') || 'doctor';

  const menuItems = [
    { path: '/dashboard', icon: Home, label: 'Overview', roles: ['doctor', 'receptionist'] },
    { path: '/admin-dashboard', icon: Shield, label: 'Admin Command', roles: ['admin'] },
    { path: '/inbox', icon: MessageSquare, label: 'Inbox', roles: ['doctor', 'receptionist', 'admin'] },
    { path: '/appointments', icon: Calendar, label: 'Schedule', roles: ['admin', 'doctor', 'receptionist'] },
    { path: '/patients', icon: Users, label: 'Patients', roles: ['admin', 'doctor', 'receptionist'] },
    { path: '/doctors', icon: Stethoscope, label: 'Doctors', roles: ['admin', 'doctor', 'receptionist'] },
    { path: '/bulk-upload', icon: UploadCloud, label: 'Add Data', roles: ['admin', 'doctor'] },
    { path: '/settings', icon: Settings, label: 'Settings', roles: ['admin', 'doctor', 'receptionist'] },
  ];

  return (
    <div className="w-80 h-screen flex flex-col p-8 z-20 relative">
      <div className="nm-flat rounded-[3rem] flex-1 flex flex-col overflow-hidden border border-white/40 p-4">
        <div className="p-8 mb-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-violet-600 flex items-center justify-center text-white shadow-xl shadow-violet-200">
              <Heart size={26} fill="white" />
            </div>
            <h1 className="text-2xl font-black text-slate-800 tracking-tighter uppercase italic">Norma</h1>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto px-4 scrollbar-thin">
          <nav className="space-y-4">
            {menuItems.filter(item => item.roles.includes(role)).map((item) => {
              const isActive = location.pathname === item.path;
              const Icon = item.icon;
              return (
                <Link 
                  key={item.path} 
                  to={item.path}
                  className="block group"
                >
                  <motion.div 
                    whileHover={{ x: 5 }}
                    className={`flex items-center gap-5 px-6 py-5 rounded-[2rem] transition-all duration-300 relative ${
                      isActive 
                        ? 'nm-inset text-violet-600 font-black' 
                        : 'text-slate-400 hover:text-slate-600'
                    }`}
                  >
                    <Icon size={22} className={isActive ? 'text-violet-600' : 'text-slate-300 group-hover:text-slate-400'} />
                    <span className="text-sm uppercase tracking-widest">{item.label}</span>
                    {isActive && (
                      <motion.div 
                        layoutId="activePill"
                        className="absolute right-6 w-2 h-2 rounded-full bg-violet-600 shadow-[0_0_12px_rgba(139,92,246,0.6)]" 
                      />
                    )}
                  </motion.div>
                </Link>
              );
            })}
          </nav>
        </div>
        
        <div className="p-8 border-t border-slate-50">
          <Link 
            to="/" 
            onClick={() => { localStorage.clear(); }}
            className="nm-button flex items-center justify-center gap-4 px-6 py-5 text-slate-400 hover:text-red-500 rounded-[2rem] transition-all group font-black uppercase tracking-widest text-[10px]"
          >
            <LogOut size={20} />
            Sign Out
          </Link>
        </div>
      </div>

      <div className="mt-8 px-8 flex items-center gap-3 opacity-30 hover:opacity-100 transition-opacity">
        <Info size={14} className="text-slate-400" />
        <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Clinical Mesh v2.5.0 Stable</p>
      </div>
    </div>
  );
}
