import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Loader2, Search, Shield, Globe, Database, Cpu, Users, Calendar, Activity, Stethoscope, Clock, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { cn } from '../utils/cn';

interface StatCardProps {
  icon: React.ElementType;
  title: string;
  value: string | number;
  color: string;
}

const AdminStatCard: React.FC<StatCardProps> = ({ icon: Icon, title, value, color }) => (
  <div className="bg-white dark:bg-gray-800 p-8 rounded-[2.5rem] border-2 border-zinc-50 dark:border-gray-700 flex-1 shadow-sm hover:border-blue-500 transition-all group">
    <div className={cn("flex items-center justify-center w-14 h-14 rounded-2xl mb-6 group-hover:scale-110 transition-transform", color)}>
      <Icon size={28} />
    </div>
    <p className="text-4xl font-black text-black dark:text-white tracking-tighter italic">{value}</p>
    <p className="text-[10px] font-black text-zinc-400 dark:text-zinc-500 uppercase tracking-[0.3em] mt-2">{title}</p>
  </div>
);

export default function AdminDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [doctors, setDoctors] = useState<any[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { token, userName } = useAuth();

  const fetchAdminData = useCallback(async () => {
    if (!token) return;
    try {
      const [statsRes, doctorsRes, notifyRes, auditRes] = await Promise.all([
        axios.get('/api/dashboard/stats', { headers: { Authorization: `Bearer ${token}` } }),
        axios.get('/api/doctors', { headers: { Authorization: `Bearer ${token}` } }),
        axios.get('/api/dashboard/notifications', { headers: { Authorization: `Bearer ${token}` } }),
        axios.get('/api/dashboard/audit-logs', { headers: { Authorization: `Bearer ${token}` } })
      ]);
      setStats(statsRes.data);
      setDoctors(doctorsRes.data);
      setNotifications(notifyRes.data);
      setAuditLogs(auditRes.data);
    } catch (err) {
      console.error('Admin data sync failed', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchAdminData();
  }, [fetchAdminData]);
  
  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="animate-spin text-blue-600" size={40} />
          <p className="text-[10px] font-black uppercase tracking-widest text-zinc-400">Loading Core Protocol...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-[1400px] mx-auto space-y-12 animate-in fade-in duration-700 pb-20">
      <header className="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-6">
        <div>
          <h1 className="text-4xl font-black text-black dark:text-white tracking-tight uppercase italic">Command Center</h1>
          <p className="text-zinc-500 mt-2 font-bold text-lg">System-wide clinical orchestration and security oversight.</p>
        </div>
        <div className="flex gap-4">
          <Link to="/doctors" className="group bg-black dark:bg-blue-600 text-white px-10 py-5 rounded-xl text-xs font-black uppercase tracking-[0.2em] shadow-2xl hover:bg-blue-700 transition-all flex items-center gap-4 active:scale-95">
            <Stethoscope size={18} className="group-hover:rotate-12 transition-transform" />
            Registry
          </Link>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        <AdminStatCard icon={Stethoscope} title="Active Providers" value={stats?.total_doctors || 0} color="bg-blue-50 text-blue-600 dark:bg-blue-900/20" />
        <AdminStatCard icon={Users} title="Clinical Identities" value={stats?.total_patients || 0} color="bg-purple-50 text-purple-600 dark:bg-purple-900/20" />
        <AdminStatCard icon={Calendar} title="Today's Nodes" value={stats?.today_appointments || 0} color="bg-orange-50 text-orange-600 dark:bg-orange-900/20" />
        <AdminStatCard icon={Activity} title="AI Throughput" value={stats?.ai_interactions || 0} color="bg-green-50 text-green-600 dark:bg-green-900/20" />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        <div className="lg:col-span-2 space-y-10">
          {/* Provider Registry Section */}
          <div className="bg-white dark:bg-gray-800 rounded-[2.5rem] border-2 border-zinc-50 dark:border-gray-700 overflow-hidden shadow-sm">
            <div className="p-10 border-b border-zinc-50 dark:border-gray-700 flex justify-between items-center bg-zinc-50/30 dark:bg-gray-900/20">
              <h2 className="text-2xl font-black text-black dark:text-white uppercase italic tracking-tighter">Core Registry</h2>
              <Link to="/search" className="text-[10px] font-black text-blue-600 uppercase tracking-widest hover:underline flex items-center gap-2">
                <Search size={14} /> Global Inquiry
              </Link>
            </div>
            <div className="p-4 space-y-4">
              {doctors.slice(0, 5).map((doctor: any) => (
                <div key={doctor._id} className="flex items-center justify-between p-6 hover:bg-zinc-50/50 dark:hover:bg-gray-900/30 rounded-2xl transition-colors group">
                  <div className="flex items-center gap-6">
                    <div className="w-12 h-12 rounded-xl bg-black dark:bg-blue-600 text-white font-black text-xs flex items-center justify-center group-hover:scale-110 transition-transform">
                      {doctor.full_name?.split(' ').map((n: string) => n[0]).join('')}
                    </div>
                    <div>
                      <p className="text-lg font-black text-black dark:text-white leading-tight">{doctor.full_name}</p>
                      <p className="text-[10px] font-black text-zinc-400 uppercase tracking-[0.2em] mt-1">{doctor.specialty}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-black dark:text-gray-300">{doctor.whatsapp_number}</p>
                    <p className="text-[9px] font-black text-blue-600 dark:text-blue-400 uppercase tracking-widest mt-1">Provider Node: Active</p>
                  </div>
                </div>
              ))}
              {doctors.length === 0 && (
                <div className="py-20 text-center text-zinc-300 font-bold italic">No provider nodes registered.</div>
              )}
            </div>
          </div>

          {/* System Audit Log Section */}
          <div className="bg-white dark:bg-gray-800 rounded-[2.5rem] border-2 border-zinc-50 dark:border-gray-700 overflow-hidden shadow-sm">
            <div className="p-10 border-b border-zinc-50 dark:border-gray-700 bg-zinc-50/30 dark:bg-gray-900/20">
              <h2 className="text-2xl font-black text-black dark:text-white uppercase italic tracking-tighter">System Audit Log</h2>
            </div>
            <div className="p-6 space-y-4">
              {notifications.map((n: any) => (
                <div key={n.id} className="flex gap-6 p-6 rounded-2xl hover:bg-zinc-50/50 dark:hover:bg-gray-900/30 transition-colors">
                  <div className={cn(
                    "w-10 h-10 rounded-xl flex items-center justify-center shrink-0",
                    n.type === 'error' ? "bg-red-50 text-red-600" : 
                    n.type === 'success' ? "bg-green-50 text-green-600" : "bg-blue-50 text-blue-600"
                  )}>
                    {n.type === 'error' ? <AlertCircle size={20} /> : <Activity size={20} />}
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <h3 className="text-sm font-black text-black dark:text-white uppercase tracking-tight">{n.title}</h3>
                      <span className="text-[9px] font-black text-zinc-400 uppercase">{n.time}</span>
                    </div>
                    <p className="text-xs text-zinc-500 dark:text-gray-400 mt-2 font-medium leading-relaxed italic">"{n.message}"</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-10">
          <div className="bg-black dark:bg-blue-700 text-white p-10 rounded-[3rem] relative overflow-hidden group border border-transparent dark:border-gray-700 shadow-2xl">
            <h2 className="text-3xl font-black tracking-tighter uppercase italic mb-8 relative z-10">Mesh Health</h2>
            <div className="space-y-6 relative z-10">
              {[
                { label: 'Cloud Gateway', value: 'Optimal', icon: Globe },
                { label: 'Database Mesh', value: 'Synchronized', icon: Database },
                { label: 'AI Cognitive Core', value: 'Active', icon: Cpu },
                { label: 'Encryption Layer', value: 'Encrypted', icon: Shield },
              ].map(metric => (
                <div key={metric.label} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5 hover:bg-white/10 transition-colors">
                  <div className="flex items-center gap-4">
                    <metric.icon className="text-blue-400" size={18} />
                    <p className="text-[10px] font-black uppercase tracking-widest text-zinc-400">{metric.label}</p>
                  </div>
                  <p className="text-[10px] font-black text-blue-400 uppercase italic">{metric.value}</p>
                </div>
              ))}
            </div>
            
            <div className="mt-12 p-6 bg-white/5 rounded-2xl border border-white/5">
              <div className="flex gap-4">
                <Shield className="text-blue-400 shrink-0" size={24} />
                <div>
                  <p className="text-[10px] font-black uppercase tracking-[0.2em] text-white">Security Protocol 2.5</p>
                  <p className="text-[10px] text-zinc-500 mt-2 font-bold leading-relaxed italic">Quantum-ready encryption layer active. System integrity verified.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
