import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, Calendar, Users, Briefcase, TrendingUp, Loader2, Plus } from 'lucide-react';
import axios from 'axios';

const mockChartData = [
  { name: 'Mon', appointments: 12 },
  { name: 'Tue', appointments: 19 },
  { name: 'Wed', appointments: 15 },
  { name: 'Thu', appointments: 25 },
  { name: 'Fri', appointments: 21 },
  { name: 'Sat', appointments: 30 },
  { name: 'Sun', appointments: 10 },
];

interface StatCardProps {
  icon: React.ElementType;
  title: string;
  value: string | number;
  change?: string;
}

const StatCard: React.FC<StatCardProps> = ({ icon: Icon, title, value, change }) => (
  <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 flex-1 shadow-sm">
    <div className="flex justify-between items-start">
      <div className="flex items-center justify-center w-12 h-12 bg-blue-50 dark:bg-blue-900/30 rounded-xl text-blue-600 dark:text-blue-400">
        <Icon size={24} />
      </div>
      {change && (
        <div className="flex items-center gap-1 text-xs font-semibold text-green-600 dark:text-green-400">
          <TrendingUp size={14} />
          <span>{change}</span>
        </div>
      )}
    </div>
    <div className="mt-4">
      <p className="text-3xl font-bold text-gray-800 dark:text-white">{value}</p>
      <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
    </div>
  </div>
);

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { token, userName } = useAuth();

  const fetchStats = useCallback(async () => {
    if (!token) return;
    try {
      const res = await axios.get('/api/dashboard/stats', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(res.data);
    } catch (err) {
      console.error('Failed to fetch dashboard stats', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="animate-spin text-blue-600" size={40} />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 dark:text-white">Welcome back, {userName}!</h1>
          <p className="text-md text-gray-500 dark:text-gray-400 mt-1">Here's a summary of your clinic's activity.</p>
        </div>
        <button className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white text-sm font-bold rounded-xl shadow-lg shadow-blue-500/25 hover:bg-blue-700 active:scale-95 transition-all">
          <Plus size={18} />
          New Appointment
        </button>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard icon={Calendar} title="Today's Appointments" value={stats?.today_appointments || 0} change="+5%" />
        <StatCard icon={Users} title="Active Patients" value={stats?.total_patients || 0} />
        <StatCard icon={Activity} title="AI Interactions" value={stats?.ai_interactions || 0} />
        <StatCard icon={Briefcase} title="Efficiency" value={stats?.efficiency || 'N/A'} />
      </div>
      
      <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
        <h2 className="text-lg font-bold text-gray-800 dark:text-white mb-6">Weekly Activity Analysis</h2>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={stats?.weekly_activity || mockChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#9ca3af" vertical={false} opacity={0.1} />
              <XAxis 
                dataKey="name" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: '#9ca3af', fontSize: 12, fontWeight: 500 }} 
                dy={10}
              />
              <YAxis 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: '#9ca3af', fontSize: 12, fontWeight: 500 }} 
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: 'none',
                  borderRadius: '1rem',
                  color: 'white',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                }}
                itemStyle={{ color: '#60a5fa' }}
              />
              <Area type="monotone" dataKey="appointments" stroke="#3b82f6" strokeWidth={3} fill="url(#colorUv)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
